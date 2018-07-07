from nflpbp_models import database, Nflpbp
import json, pprint

database.connect();


def rushing_td_stats():
	rush_query = Nflpbp.select(Nflpbp.posteam,Nflpbp.rusher,Nflpbp.rusher_id,Nflpbp.yards_gained,Nflpbp.defensiveteam,Nflpbp.gameid,Nflpbp.season).where(Nflpbp.touchdown==1, Nflpbp.rusher!='NA', Nflpbp.season=='2016').dicts()
	#rush_td_max = Nflpbp.select(Nflpbp.rusher_id, fn.Count(Nflpbp.touchdown).alias('total_touchdowns')).where(Nflpbp.touchdown==1, Nflpbp.rusher!='NA').group_by(Nflpbp.rusher_id).dicts()
	#rush_td_max_yards = Nflpbp.select(Nflpbp.rusher_id, fn.Max(Nflpbp.yards_gained).alias('longest_td')).where(Nflpbp.touchdown==1, Nflpbp.rusher!='NA').group_by(Nflpbp.rusher_id).dicts()
	

	rushing = [x for x in rush_query]
	rush_td = []
	rush_td_game = []
	for rusher_stats in rushing:
		rusher = rusher_stats['rusher_id']
		rush_not_exists = True
		for i,v in enumerate(rush_td):
			rush_dict = rush_td[i]
			if rush_dict['rusher_id'] == rusher:
				rush_not_exists = False
		rush_dict = {}
		rush_game_dict={}
		if rush_not_exists:
			rush_dict['rusher_id'] = rusher
			rush_dict['rusher'] = rusher_stats['rusher']
			rush_dict['team'] = rusher_stats['posteam']	
			count_td=0
			td_list = []
			for rusher_td_count in rushing:
				if rusher_td_count['rusher_id'] == rusher:
					td_list.append(rusher_td_count)
					count_td += 1

			rush_dict['td_count'] = count_td
			td_list.sort(key=lambda k: k['yards_gained'], reverse=True)
			rush_dict['longest_td'] = td_list[0]['yards_gained']
			rush_td.append(rush_dict)

			rush_game_dict[rusher] = [td_list]

			rush_td_game.append(rush_game_dict)



	#sorted(rush_td, key=lambda k: k['td_count'], reverse=True)
	rush_td.sort(key=lambda k: k['td_count'], reverse=True)
	#print json.dumps(rush_td)
	print pprint.pprint(rush_td)
	#print pprint.pprint(rush_td_game)

	#print rush_td_max
	#print rush_td_max_yards




	

rushing_td_stats()


