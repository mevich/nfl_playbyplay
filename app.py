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


@app.route('/')
def get_index():
    return render_template('index.html')


@app.route('/<game_id>', methods=['GET'])
def get_game_data(game_id):
    #query_object = Nflpbp.select(Nflpbp.gameid,Nflpbp.qtr,Nflpbp.timesecs,Nflpbp.playtype,Nflpbp.desc).where(Nflpbp.gameid==game_id).dicts()
    #all_data = [x for x in query_object]
    query_object = Nflpbp.select().where(Nflpbp.gameid==game_id)
    all_data = [x.to_dict() for x in query_object]
    
    data = {}
    #import pdb
    #pdb.set_trace()
    for item in all_data:
        qtr = item['qtr']
        item['yards_gained'] = float(item['yards_gained'])
        item['yrdln'] = float(item['yrdln'])
        item['ydstogo'] = float(item['ydstogo'])
        if qtr not in data:
            data[qtr] = []
        data[qtr].append(item)

    for qtr in data:
        sorted(data[qtr], key=lambda k: k['timesecs'], reverse=True)
    return jsonify(data)