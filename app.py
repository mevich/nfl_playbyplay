import json

from flask import Flask, Response, jsonify, render_template

from nflpbp_models import database, Nflpbp


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
def get_all_games_in_season(season):
    query_object = Nflpbp.select(Nflpbp.gameid,Nflpbp.game_date,Nflpbp.hometeam,Nflpbp.awayteam).distinct().where(Nflpbp.season==season).dicts()
    all_games = [x for x in query_object]
    return render_template('all_games_season.html', all_games=all_games, season=season)

@app.route('/game/<game_id>/playbyplay')
def get_index(game_id):
    return render_template('playbyplay.html', gameid=game_id)


@app.route('/game/<game_id>', methods=['GET'])
def get_game_data(game_id):
    #query_object = Nflpbp.select(Nflpbp.gameid,Nflpbp.qtr,Nflpbp.timesecs,Nflpbp.playtype,Nflpbp.desc,Nflpbp.yards_gained,Nflpbp.yrdln,Nflpbp.ydstogo,Nflpbp.yrdline100,Nflpbp.awayteam).where(Nflpbp.gameid==game_id).dicts()
    #all_data = [x for x in query_object]
    query_object = Nflpbp.select().where(Nflpbp.gameid==game_id)
    all_data = [x.to_dict() for x in query_object]
    
    data = {}
    for item in all_data:
        qtr = item['qtr']
        item['yards_gained'] = float(item['yards_gained'])
        item['yrdln'] = float(item['yrdln'])
        item['ydstogo'] = float(item['ydstogo'])
        item['yrdline100'] = float(item['yrdline100'])
        if qtr not in data:
            data[qtr] = []
        data[qtr].append(item)

    for qtr in data:
        sorted(data[qtr], key=lambda k: k['timesecs'], reverse=True)
    return jsonify(data)
