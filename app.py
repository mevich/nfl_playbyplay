import json

from flask import Flask, Response, jsonify, render_template, abort, request

from nflpbp_models import database, Nflpbp, StatsForSeason
from gather_stats import StatsEnum


app = Flask(__name__)


@app.before_request
def before_request():
    database.connect()


@app.after_request
def after_request(response):
    database.close()
    return response


@app.route("/")
def get_all_seasons():
    query_object = Nflpbp.select(Nflpbp.season).distinct().dicts()
    all_data = [x for x in query_object]
    return render_template('index.html', seasons=all_data)

@app.route("/<int:season>")
def get_season_data(season):
    return render_template('statsgame.html',season=season)


@app.route("/<int:season>/all-games")
def get_all_games_in_season(season):
    query_object = Nflpbp.select(Nflpbp.gameid,Nflpbp.season,Nflpbp.game_date,
        Nflpbp.hometeam,Nflpbp.awayteam).distinct().where(Nflpbp.season==season).dicts()
    all_games = [x for x in query_object]
    return render_template('all_games_season.html', all_games=all_games, season=season)

@app.route('/<season>/<game_id>/playbyplay')
def get_index(season, game_id):
    query_object = Nflpbp.select(Nflpbp.season,Nflpbp.hometeam,Nflpbp.awayteam).distinct().where(Nflpbp.gameid==game_id).first()
    return render_template('playbyplay.html', hometeam = query_object.hometeam,
        awayteam=query_object.awayteam, gameid=game_id, season=season)


@app.route('/<season>/<game_id>', methods=['GET'])
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


@app.route("/<season>/stats/<stats>")
def get_stats_for_season(season, stats):
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

    return render_template('stats_type.html', season=season,stats=stats,
        stats_season=stats_type_for_season)


