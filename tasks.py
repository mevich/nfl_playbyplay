import json
from utils.celery_utils import celery_object
from utils.redis_utils import redis_conn

from gather_stats import *
from utils.helpers import resize_image_square, resize_image_longest_edge
from nflpbp_models import RegisteredUsers



@celery_object.task()
def compute_all_state():
    td_stats()
    print "completed"
    return


@celery_object.task()
def get_stats_notin_redis(season, stats, redis_key):
    data = get_season_stats_async(season, stats)
    redis_conn.setex(redis_key, json.dumps(data), 60*60)
    print "DONE"
    return

@celery_object.task()
def get_stats_for_redis_sort(season, stats):
    redis_key_set = get_yards_aggregate_stats_season(season, stats)
    print 'DONE'
    return redis_key_set


@celery_object.task()
def get_season_stats_charts_redis(season, stats, redis_key):
    chart_data = get_season_stats_charts_data(season, stats)
    redis_conn.setex(redis_key, json.dumps(chart_data), 60*60)
    print "DONE"
    return


@celery_object.task()
def do_resize_image_square(user_id):
    image_name = (RegisteredUsers.select(RegisteredUsers.image_name).where(RegisteredUsers.id==user_id).first()).image_name
    resize_image_square(image_name, 500)
    return

@celery_object.task()
def do_resize_image_longest(user_id):
    image_name = (RegisteredUsers.select(RegisteredUsers.image_name).where(RegisteredUsers.id==user_id).first()).image_name
    resize_image_longest_edge(image_name,1000)
    return

@celery_object.task()
def get_all_seasons_redis(redis_key):
    query_object = Nflpbp.select(Nflpbp.season).distinct().dicts()
    all_seasons = [x for x in query_object]
    redis_conn.setex(redis_key, json.dumps(all_seasons), 60*60)
    return
