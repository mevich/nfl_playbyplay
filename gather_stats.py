from nflpbp_models import *
import json, pprint
from enum import Enum
from utils.redis_utils import redis_conn


class StatsEnum(Enum):
    rushing=1
    passing=2
    receiving=3

# class StatsEnum(Enum):
#   def __init__(self,stats):
#       if self.stats=='rushing':
#           rushing=1
#       elif self.stats=='passing':
#           passing=2
#       elif self.stats=='receiving':
#           receiving=3


def get_aggregate_stats(stats):
    #database.connect()
    if stats=='rushing':
        stats_query = Nflpbp.select(Nflpbp.posteam,Nflpbp.rusher,Nflpbp.rusher_id,Nflpbp.yards_gained,Nflpbp.defensiveteam,Nflpbp.gameid,Nflpbp.season).where(Nflpbp.touchdown==1,Nflpbp.rusher!='NA',Nflpbp.rusher_id!='None',~(Nflpbp.desc.contains('%REVERSED%')), ~(Nflpbp.desc.contains('%NULLIFIED%'))).dicts()
    #rush_td_max = Nflpbp.select(Nflpbp.rusher_id, fn.Sum(Nflpbp.touchdown).alias('total_touchdowns')).where(Nflpbp.touchdown==1, Nflpbp.rusher!='NA').group_by(Nflpbp.rusher_id).dicts()
    #rush_td_max_yards = Nflpbp.select(Nflpbp.rusher_id, fn.Max(Nflpbp.yards_gained).alias('longest_td')).where(Nflpbp.touchdown==1, Nflpbp.rusher!='NA').group_by(Nflpbp.rusher_id).dicts()
        total_stats_query = Nflpbp.select(Nflpbp.season, Nflpbp.rusher_id, Nflpbp.rusher, Nflpbp.posteam, 
            fn.SUM(Nflpbp.yards_gained).alias('total_yards'), fn.Count(Nflpbp.rusher_id).alias('total_attempts')).where((Nflpbp.rusher!='NA') & (Nflpbp.rusher_id!='None') 
            & ((Nflpbp.accepted_penalty==0) | ((Nflpbp.accepted_penalty==1) & (Nflpbp.posteam!=Nflpbp.penalizedteam)))).group_by(Nflpbp.season,Nflpbp.rusher_id,Nflpbp.rusher).dicts()
    elif stats=='passing':          
        stats_query = Nflpbp.select(Nflpbp.posteam,Nflpbp.passer,Nflpbp.passer_id,Nflpbp.yards_gained,Nflpbp.defensiveteam,Nflpbp.gameid,Nflpbp.season).where(Nflpbp.touchdown==1,Nflpbp.passer!='NA',Nflpbp.passer_id!='NA',~(Nflpbp.desc.contains('%REVERSED%')), ~(Nflpbp.desc.contains('%NULLIFIED%'))).dicts()
        total_stats_query = Nflpbp.select(Nflpbp.season, Nflpbp.passer_id, Nflpbp.passer, Nflpbp.posteam, 
            fn.SUM(Nflpbp.yards_gained).alias('total_yards'), fn.Count(Nflpbp.passer_id).alias('total_attempts')).where((Nflpbp.passer!='NA') & (Nflpbp.passer_id!='None') 
            & ((Nflpbp.accepted_penalty==0) | ((Nflpbp.accepted_penalty==1) & (Nflpbp.posteam!=Nflpbp.penalizedteam)))).group_by(Nflpbp.season,Nflpbp.passer_id,Nflpbp.passer).dicts()
    elif stats=='receiving':
        stats_query = Nflpbp.select(Nflpbp.posteam,Nflpbp.receiver,Nflpbp.receiver_id,Nflpbp.yards_gained,Nflpbp.defensiveteam,Nflpbp.gameid,Nflpbp.season).where(Nflpbp.touchdown==1,Nflpbp.receiver!='NA',Nflpbp.receiver_id!='NA',~(Nflpbp.desc.contains('%REVERSED%')), ~(Nflpbp.desc.contains('%NULLIFIED%'))).dicts()
        total_stats_query = Nflpbp.select(Nflpbp.season, Nflpbp.receiver_id, Nflpbp.receiver, Nflpbp.posteam, 
            fn.SUM(Nflpbp.yards_gained).alias('total_yards'), fn.Count(Nflpbp.receiver_id).alias('total_attempts')).where((Nflpbp.receiver!='NA') & (Nflpbp.receiver_id!='None') 
            & ((Nflpbp.accepted_penalty==0) | ((Nflpbp.accepted_penalty==1) & (Nflpbp.posteam!=Nflpbp.penalizedteam)))).group_by(Nflpbp.season,Nflpbp.receiver_id, Nflpbp.receiver).dicts()

    stats_season_dict={}
    stats_all_player = []
    stats_season_obj = [x for x in stats_query]

    total_stats_query_obj = [x for x in total_stats_query]

    for seasons in stats_season_obj:
        season_not_exists = True
        stats_season = seasons['season']
        try:
            if stats_season_dict[stats_season] != []:
                season_not_exists = False
        except:
            1==1
        if season_not_exists:
            stats_type_obj = [x for x in stats_season_obj if x['season']==stats_season]
            stat_all = []
            for stats_type in stats_type_obj:
                if stats=='rushing':
                    stats_type_for_name = 'rusher'
                    stats_type_for_id = 'rusher_id'
                    stats_type_for = stats_type[stats_type_for_id]
                    stat_type=StatsEnum.rushing.value
                elif stats=='passing':
                    stats_type_for_name = 'passer'
                    stats_type_for_id = 'passer_id'
                    stats_type_for = stats_type[stats_type_for_id]
                    stat_type=StatsEnum.passing.value
                elif stats=='receiving':
                    stats_type_for_name = 'receiver'
                    stats_type_for_id = 'receiver_id'
                    stats_type_for = stats_type[stats_type_for_id]
                    stat_type=StatsEnum.receiving.value
                stats_for_not_exists = True
                for i,v in enumerate(stat_all):
                    stats_dict = stat_all[i]
                    if stats_dict[stats_type_for_id] == stats_type_for:
                        stats_for_not_exists = False
                stats_dict = {}
                # stats_all_player_dict={}
                if stats_for_not_exists:
                    stats_dict['season'] = stats_season
                    stats_dict[stats_type_for_id] = stats_type_for
                    stats_dict[stats_type_for_name] = stats_type[stats_type_for_name]
                    stats_dict['team'] = stats_type['posteam']  
                    count_td=0
                    td_list = []
                    for stats_td_count in stats_type_obj:
                        if stats_td_count[stats_type_for_id] == stats_type_for:
                            td_list.append(stats_td_count)
                            count_td += 1

                    stats_dict['td_count'] = count_td
                    td_list.sort(key=lambda k: k['yards_gained'], reverse=True)
                    stats_dict['longest_td'] = td_list[0]['yards_gained']
                    for total_stats_type in total_stats_query_obj:
                        if (total_stats_type[stats_type_for_name] == stats_dict[stats_type_for_name] and 
                                total_stats_type[stats_type_for_id] == stats_dict[stats_type_for_id] and 
                                total_stats_type['season'] == stats_season):
                            stats_dict['total_yards'] = total_stats_type['total_yards']
                            stats_dict['total_attempts'] = total_stats_type['total_attempts']
                    stats_player_data = (stat_type, stats_season, stats_type_for, stats_type[stats_type_for_name], stats_dict)
                    stats_all_player.append(stats_player_data)

                    stat_all.append(stats_dict)


            stat_all.sort(key=lambda k: k['td_count'], reverse=True)
            stats_season_dict[stats_season] = stat_all

    with database:
        database.create_tables([StatsForSeason, PlayerStatsForSeason])

    for season in stats_season_dict:
        if stats=='rushing':
            StatsForSeason.create(stat_type=StatsEnum.rushing.value, 
                season=season,stats_for_season=json.dumps(stats_season_dict[season]))
        elif stats=='passing':
            StatsForSeason.create(stat_type=StatsEnum.passing.value, 
                season=season,stats_for_season=json.dumps(stats_season_dict[season]))
        elif stats=='receiving':
            StatsForSeason.create(stat_type=StatsEnum.receiving.value, 
                season=season,stats_for_season=json.dumps(stats_season_dict[season]))

    fields = [PlayerStatsForSeason.stat_type, PlayerStatsForSeason.season, 
        PlayerStatsForSeason.player_id, PlayerStatsForSeason.player_name, PlayerStatsForSeason.stats_for_season]
    PlayerStatsForSeason.insert_many(stats_all_player, fields=fields).execute()


def get_season_stats_async(season,stats):
    if stats=='rushing':
        stats_for_season_qry_obj = StatsForSeason.select(StatsForSeason.stats_for_season).where(StatsForSeason.stat_type==StatsEnum.rushing.value, 
            StatsForSeason.season==season).first()
    elif stats=='passing':
        stats_for_season_qry_obj = StatsForSeason.select(StatsForSeason.stats_for_season).where(StatsForSeason.stat_type==StatsEnum.passing.value, 
            StatsForSeason.season==season).first()
    elif stats=='receiving':
        stats_for_season_qry_obj = StatsForSeason.select(StatsForSeason.stats_for_season).where(StatsForSeason.stat_type==StatsEnum.receiving.value, 
            StatsForSeason.season==season).first()

    return json.loads(stats_for_season_qry_obj.stats_for_season)

    # database.close()


def get_yards_aggregate_stats(stats):
    if stats=='rushing':
        total_stats_query = Nflpbp.select(Nflpbp.season, Nflpbp.rusher_id, Nflpbp.rusher, Nflpbp.posteam, 
            fn.SUM(Nflpbp.yards_gained).alias('total_yards'), fn.Count(Nflpbp.rusher_id).alias('total_attempts')).where((Nflpbp.rusher!='NA') & (Nflpbp.rusher_id!='None') 
            & ((Nflpbp.accepted_penalty==0) | ((Nflpbp.accepted_penalty==1) & (Nflpbp.posteam!=Nflpbp.penalizedteam)))).group_by(Nflpbp.season,Nflpbp.rusher_id,Nflpbp.rusher).dicts()
        table_name = RushStatsForSeason
    elif stats=='passing':
      total_stats_query = Nflpbp.select(Nflpbp.season, Nflpbp.passer_id, Nflpbp.passer, Nflpbp.posteam, 
            fn.SUM(Nflpbp.yards_gained).alias('total_yards'), fn.Count(Nflpbp.passer_id).alias('total_attempts')).where((Nflpbp.passer!='NA') & (Nflpbp.passer_id!='None') 
            & ((Nflpbp.accepted_penalty==0) | ((Nflpbp.accepted_penalty==1) & (Nflpbp.posteam!=Nflpbp.penalizedteam)))).group_by(Nflpbp.season,Nflpbp.passer_id,Nflpbp.passer).dicts()
      table_name = PassStatsForSeason
    elif stats=='receiving':
      total_stats_query = Nflpbp.select(Nflpbp.season, Nflpbp.receiver_id, Nflpbp.receiver, Nflpbp.posteam, 
            fn.SUM(Nflpbp.yards_gained).alias('total_yards'), fn.Count(Nflpbp.receiver_id).alias('total_attempts')).where((Nflpbp.receiver!='NA') & (Nflpbp.receiver_id!='None') 
            & ((Nflpbp.accepted_penalty==0) | ((Nflpbp.accepted_penalty==1) & (Nflpbp.posteam!=Nflpbp.penalizedteam)))).group_by(Nflpbp.season,Nflpbp.receiver_id, Nflpbp.receiver).dicts()
      table_name = ReceiveStatsForSeason


    total_stats_query_obj = [x for x in total_stats_query]

    with database:
        database.create_tables([table_name])

    for stats_for in total_stats_query_obj:
        if stats=='rushing':
            table_name.create(season=stats_for['season'], rusher=stats_for['rusher'], rusher_id=stats_for['rusher_id'], total_attempts = stats_for['total_attempts'], total_yards=stats_for['total_yards'])
        elif stats=='passing':
            table_name.create(season=stats_for['season'], passer=stats_for['passer'], passer_id=stats_for['passer_id'], total_attempts = stats_for['total_attempts'], total_yards=stats_for['total_yards'])
        elif stats=='receiving':
            table_name.create(season=stats_for['season'], receiver=stats_for['receiver'], receiver_id=stats_for['receiver_id'], total_attempts = stats_for['total_attempts'], total_yards=stats_for['total_yards'])

    # database.close()

def get_yards_aggregate_stats_season(season, stats):
    if stats=='rushing':
        table_name = RushStatsForSeason
        aggr_stats_qry = table_name.select(table_name.rusher, table_name.total_yards).where(table_name.season==season)
    elif stats=='passing':
        table_name = PassStatsForSeason
        aggr_stats_qry = table_name.select(table_name.passer, table_name.total_yards).where(table_name.season==season)
    elif stats=='receiving':
        table_name = ReceiveStatsForSeason
        aggr_stats_qry = table_name.select(table_name.receiver, table_name.total_yards).where(table_name.season==season)

    aggr_stats_qry_obj = [x for x in aggr_stats_qry.tuples()]

    zset_name = "{}_leader_season_{}".format(stats, season)
    value_score = dict(aggr_stats_qry_obj)
    redis_conn.zadd(zset_name, **value_score)

    return zset_name


def get_season_stats_charts_data(season, stats):
    if stats=='rushing':
        table_name = RushStatsForSeason
        aggr_stats_qry = table_name.select(table_name.rusher, table_name.total_yards, table_name.total_attempts).where(table_name.season==season)
    elif stats=='passing':
        table_name = PassStatsForSeason
        aggr_stats_qry = table_name.select(table_name.passer, table_name.total_yards, table_name.total_attempts).where(table_name.season==season)
    elif stats=='receiving':
        table_name = ReceiveStatsForSeason
        aggr_stats_qry = table_name.select(table_name.receiver, table_name.total_yards, table_name.total_attempts).where(table_name.season==season)

    aggr_stats_qry_obj = [{'name': x[0], 'total_yards': x[1], 'total_attempts': x[2]} for x in aggr_stats_qry.tuples()]

    return aggr_stats_qry_obj


