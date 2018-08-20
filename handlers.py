import json, time, uuid
from flask import Response, jsonify, render_template, abort, request, make_response, flash, redirect
from celery.result import AsyncResult
from werkzeug.datastructures import CombinedMultiDict

from app import app
from tasks import *
from nflpbp_models import *
from gather_stats import StatsEnum
from utils.redis_utils import redis_conn
from wtforms import TextField, Form, validators
from ast import literal_eval
from forms import RegisterForm
from utils.helpers import *
import hashlib
from utils.config import *
from datetime import datetime
from datetime import timedelta
from collections import Counter
import numpy as np


@app.route('/register/', methods=['GET'])
def get_register():
    form = RegisterForm()
    return render_template('form.html', form=form)


@app.route("/register/", methods=['POST'])
def post_register():
    data = CombinedMultiDict((request.files, request.form))
    form = RegisterForm(data)
    if form.validate():
        image_object = form.image_upload.data
        hashed_image = hashlib.md5(image_object.read()).hexdigest()
        hashed_image_key = 'originals/{}'.format(hashed_image)
        upload_file_to_s3(image_object, hashed_image_key)
        db_entry = RegisteredUsers.create(email=form.data['email'], password=form.data['password'], image_name=hashed_image)

        do_resize_image_square.delay(db_entry.id)
        do_resize_image_longest.delay(db_entry.id)

        image_url_profile = '{}1000px/{}'.format(S3_LOCATION, image_name)

        # return render_template('profile.html', email=form.data['email'], image_url=image_url_profile)

        # resize_image_longest_edge(hashed_image,1000)
        # resize_image_square(hashed_image, 500)
        
        if request.is_xhr:
            return jsonify({'success': True, 'message':('User {} created by ajax request').format(form.data['email'])})
        else:
            return 'User {} was created'.format(form.data['email'])
    else:
        print form.errors
        return render_template('form.html', form=form)


@app.route("/")
def get_all_seasons():
    redis_key = "seasons"
    data = redis_conn.get(redis_key)
    if data:
        print json.loads(data)
        return render_template('index.html', seasons=json.loads(data))
    else:
        celery_worker_job = get_all_seasons_redis.delay(redis_key)
        celery_worker_job.wait()        
        if celery_worker_job.status == 'SUCCESS':
            return get_all_seasons()


@app.route("/dropdown/", methods=['GET'])
def get_all_seasons_dropdown():
    redis_key = "seasons"
    data = redis_conn.get(redis_key)
    if data:
        return jsonify(json.loads(data))
    else:
        celery_worker_job = get_all_seasons_redis.delay(redis_key)
        celery_worker_job.wait()        
        if celery_worker_job.status == 'SUCCESS':
            return get_all_seasons_dropdown()

@app.route("/<int:season>/")
def get_season_data(season):
    return render_template('statsgame.html',season=season)


@app.route("/<int:season>/all-games/")
def get_all_games_in_season(season):
    query_object = Nflpbp.select(Nflpbp.gameid,Nflpbp.season,Nflpbp.game_date,
        Nflpbp.hometeam,Nflpbp.awayteam).distinct().where(Nflpbp.season==season).dicts()
    all_games = [x for x in query_object]
    sorted(all_games, key=lambda k: k['game_date'])

    date_count = Counter([x['game_date'] for x in all_games])
    week_date = [k for k,v in date_count.iteritems() if v>3]
    week_date.sort()
    dates = [k for k,v in date_count.iteritems()]
    dates.sort()
    weekly = [x.setdefault('week', (week_date.index(y) + 1)) 
        for x in all_games for y in week_date 
            if x['game_date'] in [y, y+timedelta(days=2), y+timedelta(days=1), y-timedelta(days=1), y-timedelta(days=3), y-timedelta(days=4)]]
    weeks = [n for n in np.unique(weekly)]

    all_weeks = []
    for w in weeks:
        week = {}
        week['week'] = w
        game_data = []
        week['game_data'] = game_data
        for d in week_date:
            for date in dates:
                if w == (week_date.index(d) + 1) and date in [d, d+timedelta(days=2), d+timedelta(days=1), d-timedelta(days=1), d-timedelta(days=3), d-timedelta(days=4)]:
                    game_dict = {}
                    game_dict['game_date'] = date.strftime('%A %b %d %Y')
                    games = []
                    game_dict['games'] = games
                    [games.append(game) for game in all_games if game['game_date'] == date and game['week'] == w]

                    game_data.append(game_dict)

        all_weeks.append(week)

    return render_template('all_games_season.html', all_games=all_weeks, season=season)

@app.route('/<season>/<game_id>/playbyplay/')
def get_index(season, game_id):
    query_object = Nflpbp.select(Nflpbp.season,Nflpbp.game_date, Nflpbp.hometeam,Nflpbp.awayteam).distinct().where(Nflpbp.gameid==game_id).first()
    # game_date = datetime.strptime(str(query_object.game_date), '%Y-%m-%d').strftime('%b %d %Y')
    game_date = (query_object.game_date).strftime('%b %d %Y')
    return render_template('playbyplay.html', hometeam = query_object.hometeam,
        awayteam=query_object.awayteam, gameid=game_id, game_date=game_date, season=season, gmaps_api=GMAPS_API)


@app.route('/<season>/<game_id>/', methods=['GET'])
def get_game_data(season, game_id):
    #query_object = Nflpbp.select(Nflpbp.gameid,Nflpbp.qtr,Nflpbp.timesecs,Nflpbp.playtype,Nflpbp.desc,Nflpbp.yards_gained,Nflpbp.yrdln,Nflpbp.ydstogo,Nflpbp.yrdline100,Nflpbp.awayteam).where(Nflpbp.gameid==game_id).dicts()
    #all_data = [x for x in query_object]
    query_object = Nflpbp.select().where(Nflpbp.season==season, Nflpbp.gameid==game_id)
    all_data = [x.to_dict() for x in query_object]
    data = {}
    for item in all_data:
        qtr = item['qtr']
        try:
            item['yards_gained'] = float(item['yards_gained'])
            item['yrdln'] = float(item['yrdln'])
            item['ydstogo'] = float(item['ydstogo'])
            item['yrdline100'] = float(item['yrdline100'])
        except:
            1==1
        if qtr not in data:
            data[qtr] = []
        data[qtr].append(item)

    for qtr in data:
        sorted(data[qtr], key=lambda k: k['timesecs'], reverse=True)
    return jsonify(data)


@app.route("/<season>/stats/<stats>/")
def get_stats_for_season(season, stats):
    print request.cookies
    sort_by = request.args.get("sort", "td_count")
    # import pdb
    # pdb.set_trace()
    if stats=='rushing':
        stats_type_season = StatsForSeason.select(
            StatsForSeason.stats_for_season).where(
            StatsForSeason.season==season, StatsForSeason.stat_type==StatsEnum.rushing.value).first()
    elif stats=='passing':
        stats_type_season = StatsForSeason.select(
            StatsForSeason.stats_for_season).where(
            StatsForSeason.season==season, StatsForSeason.stat_type==StatsEnum.passing.value).first()
    elif stats=='receiving':
        stats_type_season = StatsForSeason.select(
            StatsForSeason.stats_for_season).where(
            StatsForSeason.season==season, StatsForSeason.stat_type==StatsEnum.receiving.value).first()
    stats_type_for_season = json.loads(stats_type_season.stats_for_season)
    stats_type_for_season.sort(key=lambda k: k[sort_by], reverse=True)

    if request.is_xhr:
        return render_template('stats_type_table.html', stats_season=stats_type_for_season,
            stats=stats)

    response =  make_response(render_template('stats_type.html', season=season,stats=stats,
        stats_season=stats_type_for_season))
    # response.set_cookie('cookie_name',value=uuid.uuid4().hex)
    return response


@app.route("/stats/<season>/<stats>/")
def get_blank_page(season,stats):
    return render_template('redis_check.html', season=season, stats=stats)


@app.route("/stats/<season>/<stats>/data/")
def get_redis_celery_data(season, stats):
    redis_key = "{}-{}".format(season, stats)
    data = redis_conn.get(redis_key)
    # import pdb; pdb.set_trace()
    if data:
        stats_season = json.loads(data)
        html = render_template("stats_type_table.html", stats_season=stats_season, stats=stats)
        return jsonify({"status": "success", "html": html})
    else:
        celery_worker_job = get_stats_notin_redis.delay(season, stats, redis_key)
        return jsonify({"status": "pending", "job_id": celery_worker_job.id})


@app.route("/job/<job_id>/")
def get_job_status(job_id):
    res = AsyncResult(job_id, backend=celery_object.backend)
    return jsonify({"status": res.ready()})


@app.route("/stats/<season>/<stats>/charts/")
def get_season_stats_charts(season, stats):
    redis_key = "charts:{}-{}".format(season, stats)
    data = redis_conn.get(redis_key)
    if data:
        charts_stats_season = json.loads(data)
        # charts_stats_season = data
        return render_template('stats_chart.html', stats=stats, season=season, stats_data=charts_stats_season)
    else:
        celery_worker_job = get_season_stats_charts_redis.delay(season, stats, redis_key)
        celery_worker_job.wait()        
        if celery_worker_job.status == 'SUCCESS':
            return get_season_stats_charts(season, stats)

class SearchForm(Form):
    player_search = TextField('Enter Player Name', id='player_search')


@app.route('/players/autocomplete/search/', methods=['GET', 'POST'])
def get_autocomplete_form():
    form = SearchForm(request.form)
    return render_template("autocomplete.html", form=form)


@app.route('/players/autocomplete/', methods=['GET'])
def get_autocomplete():
    search_by = request.args.get("term", '')
    players = PlayerStatsForSeason.select(PlayerStatsForSeason.player_name).distinct().where(PlayerStatsForSeason.player_name.contains('%' + search_by)).tuples()
    names = [x[0] for x in players]
    return jsonify(names)

@app.route('/players/autocomplete/data/', methods=['GET'])
def get_autocomplete_data():
    player_name = request.args.get("term", '')
    all_stats_for_player = get_player_data(player_name)
    return render_template('player_data.html', name=player_name, player_stats=all_stats_for_player)

@app.route('/players/autocomplete/charts/', methods=['GET'])
def get_autocomplete_charts():
    player_name = request.args.get("term", '')
    all_stats_for_player = get_player_data(player_name)
    return render_template('player_charts.html', name=player_name, player_stats=all_stats_for_player)

@app.route('/players', methods=['GET'])
def get_player_data():
    player_name = request.args.get('q', '')
    stats_for_season_obj = PlayerStatsForSeason.select(PlayerStatsForSeason.stats_for_season, PlayerStatsForSeason.stat_type, PlayerStatsForSeason.season).distinct().where(PlayerStatsForSeason.player_name==player_name).tuples()
    # stats_for_season_data = [literal_eval(x[0]) for x in stats_for_season_obj]
    all_stats_for_player=[]
    
    for x in stats_for_season_obj:
        all_stats_for_season={}
        season_not_exists = False
        if all_stats_for_player:
            if x[2] not in [p['season'] for p in all_stats_for_player]:
                    all_stats_for_season['season']=x[2]
                    all_stats_for_season['rushing'] = [literal_eval(a[0]) for a in stats_for_season_obj if (a[2]==all_stats_for_season['season'] and a[1]==1)]
                    all_stats_for_season['passing'] = [literal_eval(a[0]) for a in stats_for_season_obj if (a[2]==all_stats_for_season['season'] and a[1]==2)]
                    all_stats_for_season['receiving'] = [literal_eval(a[0]) for a in stats_for_season_obj if (a[2]==all_stats_for_season['season'] and a[1]==3)]
        else:
            all_stats_for_season['season']=x[2]
            all_stats_for_season['rushing'] = [literal_eval(a[0]) for a in stats_for_season_obj if (a[2]==all_stats_for_season['season'] and a[1]==1)]
            all_stats_for_season['passing'] = [literal_eval(a[0]) for a in stats_for_season_obj if (a[2]==all_stats_for_season['season'] and a[1]==2)]
            all_stats_for_season['receiving'] = [literal_eval(a[0]) for a in stats_for_season_obj if (a[2]==all_stats_for_season['season'] and a[1]==3)]

        if all_stats_for_season:
            all_stats_for_player.append(all_stats_for_season)
            all_stats_for_player.sort(key=lambda k:k['season'])

    return render_template('player_page.html', name=player_name, player_stats=all_stats_for_player)
    # return all_stats_for_player
