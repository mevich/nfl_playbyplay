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
from utils.config_local import *

session_cookie_name = 'football_stats_sess'



@app.before_request
def before_request():
    request.session = Session.get(request.cookies.get(session_cookie_name, ''))


def create_session_table():
    with database:
        database.create_tables([SessionTable])

class Session(object):
    @classmethod
    def create(cls, data):
        session_id = uuid.uuid4().hex
        SessionTable.create(session_id=session_id, body=json.dumps(data))
        return session_id

    @classmethod
    def get(cls, session_id):
        try:
            session_row = SessionTable.get(SessionTable.session_id==session_id)
            return session_row.data
        except SessionTable.DoesNotExist:
            return None

    @classmethod
    def update(cls, session_id, new_data):
        curr_data = cls.get(session_id)
        if not curr_data: return
        curr_data.update(new_data)
        upd_data = json.dumps(curr_data)
        return SessionTable.update(body=upd_data).where(SessionTable.session_id==session_id).execute()

    @classmethod
    def delete(cls, session_id):
        return SessionTable.delete().where(SessionTable.session_id==session_id).execute()


@app.route('/')
def get_home():
    if request.session:
        return "Hello Boss!"
    else:
        return render_template('login.html')

    # When a session is created, 
 
@app.route('/login/', methods=['GET','POST'])
def do_admin_login():
    if request.form.get('password') == 'password' and request.form.get('username') == 'admin':
        user_data = {"user_id": 1}
        session_id = Session.create(user_data)
        flash('Login Successful!')
        response = make_response(redirect("/"))
        response.set_cookie(session_cookie_name, value=session_id)
        return response
    else:
        flash('wrong password!')
        return render_template('login.html')

@app.route('/logout/', methods=['GET','POST'])
def do_logout():
    response = make_response(render_template('logout.html'))
    response.delete_cookie(session_cookie_name)
    Session.delete(request.session)
    return response


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

        return render_template('profile.html', email=form.data['email'], image_url=image_url_profile)

        # resize_image_longest_edge(hashed_image,1000)
        # resize_image_square(hashed_image, 500)
        
        # if request.is_xhr:
        #     return jsonify({'success': True, 'message':('User {} created by ajax request').format(form.data['email'])})
        # else:
        #     return 'User {} was created'.format(form.data['email'])
    else:
        print form.errors
        return render_template('form.html', form=form)


@app.route("/all_seasons/")
def get_all_seasons():
    query_object = Nflpbp.select(Nflpbp.season).distinct().dicts()
    all_data = [x for x in query_object]
    return render_template('index.html', seasons=all_data)

@app.route("/<int:season>/")
def get_season_data(season):
    return render_template('statsgame.html',season=season)


@app.route("/<int:season>/all-games/")
def get_all_games_in_season(season):
    query_object = Nflpbp.select(Nflpbp.gameid,Nflpbp.season,Nflpbp.game_date,
        Nflpbp.hometeam,Nflpbp.awayteam).distinct().where(Nflpbp.season==season).dicts()
    all_games = [x for x in query_object]
    return render_template('all_games_season.html', all_games=all_games, season=season)

@app.route('/<season>/<game_id>/playbyplay/')
def get_index(season, game_id):
    query_object = Nflpbp.select(Nflpbp.season,Nflpbp.hometeam,Nflpbp.awayteam).distinct().where(Nflpbp.gameid==game_id).first()
    return render_template('playbyplay.html', hometeam = query_object.hometeam,
        awayteam=query_object.awayteam, gameid=game_id, season=season)


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
    rushers = PlayerStatsForSeason.select(PlayerStatsForSeason.player_name).distinct().where(PlayerStatsForSeason.player_name.contains('%' + search_by)).tuples()
    names = [x[0] for x in rushers]
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


def get_player_data(player_name):
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

    return all_stats_for_player
