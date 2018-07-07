from nflpbp_models import database, Nflpbp, StatsForSeason
import json, pprint
from enum import Enum


class StatsEnum(Enum):
	rushing=1
	passing=2
	receiving=3

# class StatsEnum(Enum):
# 	def __init__(self,stats):
# 		if self.stats=='rushing':
# 			rushing=1
# 		elif self.stats=='passing':
# 			passing=2
# 		elif self.stats=='receiving':
# 			receiving=3

def td_stats(stats):
	#database.connect()
	if stats=='rushing':
		stats_query = Nflpbp.select(Nflpbp.posteam,Nflpbp.rusher,Nflpbp.rusher_id,Nflpbp.yards_gained,Nflpbp.defensiveteam,Nflpbp.gameid,Nflpbp.season).where(Nflpbp.touchdown==1,Nflpbp.rusher!='NA',~(Nflpbp.desc.contains('%REVERSED%'))).dicts()
	#rush_td_max = Nflpbp.select(Nflpbp.rusher_id, fn.Count(Nflpbp.touchdown).alias('total_touchdowns')).where(Nflpbp.touchdown==1, Nflpbp.rusher!='NA').group_by(Nflpbp.rusher_id).dicts()
	#rush_td_max_yards = Nflpbp.select(Nflpbp.rusher_id, fn.Max(Nflpbp.yards_gained).alias('longest_td')).where(Nflpbp.touchdown==1, Nflpbp.rusher!='NA').group_by(Nflpbp.rusher_id).dicts()
	elif stats=='passing':			
		stats_query = Nflpbp.select(Nflpbp.posteam,Nflpbp.passer,Nflpbp.passer_id,Nflpbp.yards_gained,Nflpbp.defensiveteam,Nflpbp.gameid,Nflpbp.season).where(Nflpbp.touchdown==1,Nflpbp.passer!='NA',~(Nflpbp.desc.contains('%REVERSED%'))).dicts()
	elif stats=='receiving':
		stats_query = Nflpbp.select(Nflpbp.posteam,Nflpbp.receiver,Nflpbp.receiver_id,Nflpbp.yards_gained,Nflpbp.defensiveteam,Nflpbp.gameid,Nflpbp.season).where(Nflpbp.touchdown==1,Nflpbp.receiver!='NA',~(Nflpbp.desc.contains('%REVERSED%'))).dicts()

	stats_season_dict={}
	stats_season_obj = [x for x in stats_query]

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
			stat_td = []
			# rush_td_game = []
			for stats_type in stats_type_obj:
				if stats=='rushing':
					stats_type_for_name = 'rusher'
					stats_type_for_id = 'rusher_id'
					stats_type_for = stats_type[stats_type_for_id]
				elif stats=='passing':
					stats_type_for_name = 'passer'
					stats_type_for_id = 'passer_id'
					stats_type_for = stats_type[stats_type_for_id]
				elif stats=='receiving':
					stats_type_for_name = 'receiver'
					stats_type_for_id = 'receiver_id'
					stats_type_for = stats_type[stats_type_for_id]
				stats_for_not_exists = True
				for i,v in enumerate(stat_td):
					stats_dict = stat_td[i]
					if stats_dict[stats_type_for_id] == stats_type_for:
						stats_for_not_exists = False
				stats_dict = {}
				# rush_game_dict={}
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
					stat_td.append(stats_dict)

					# rush_game_dict[rusher] = [td_list]

					# rush_td_game.append(rush_game_dict)



			#sorted(rush_td, key=lambda k: k['td_count'], reverse=True)
			stat_td.sort(key=lambda k: k['td_count'], reverse=True)
			#print json.dumps(rush_td)
			#print pprint.pprint(rush_td)
			#print pprint.pprint(rush_td_game)

			stats_season_dict[stats_season] = stat_td

		#return rushing_season

	# rush_stats_for_season = rushing_td_stats()
	# print pprint.pprint(rush_stats_for_season)
	with database:
		database.create_tables([StatsForSeason])
	# Rushing_stats_season.create_table()

	for season in stats_season_dict:
		# StatsForSeason.create(stat_type=StatsEnum.stats.value, season=season,stats_for_season=json.dumps(stats_season_dict[season]))
		if stats=='rushing':
			StatsForSeason.create(stat_type=StatsEnum.rushing.value, 
                season=season,stats_for_season=json.dumps(stats_season_dict[season]))
		elif stats=='passing':
			StatsForSeason.create(stat_type=StatsEnum.passing.value, 
                season=season,stats_for_season=json.dumps(stats_season_dict[season]))
		elif stats=='receiving':
			StatsForSeason.create(stat_type=StatsEnum.receiving.value, 
                season=season,stats_for_season=json.dumps(stats_season_dict[season]))

		# rush_db_entry = Rushing_stats_season(season=season,rushing_stats=rush_stats_for_season[season])
		# rush_db_entry.save()
    # database.close()


