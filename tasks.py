import json
from utils.celery_utils import celery_object
from utils.redis_utils import redis_conn

from gather_stats import *



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
