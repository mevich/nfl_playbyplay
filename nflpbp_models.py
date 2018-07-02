from peewee import *

database = SqliteDatabase('nfl.db', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Nflpbp(BaseModel):
    absscorediff = TextField(column_name='AbsScoreDiff', null=True)
    accepted_penalty = TextField(column_name='Accepted_Penalty', null=True)
    airyards = TextField(column_name='AirYards', null=True)
    awayteam = TextField(column_name='AwayTeam', null=True)
    awaytimeouts_remaining_post = TextField(column_name='AwayTimeouts_Remaining_Post', null=True)
    awaytimeouts_remaining_pre = TextField(column_name='AwayTimeouts_Remaining_Pre', null=True)
    away_wp_post = TextField(column_name='Away_WP_post', null=True)
    away_wp_pre = TextField(column_name='Away_WP_pre', null=True)
    blockingplayer = TextField(column_name='BlockingPlayer', null=True)
    chalreplayresult = TextField(column_name='ChalReplayResult', null=True)
    challenge_replay = TextField(column_name='Challenge_Replay', null=True)
    defteamscore = TextField(column_name='DefTeamScore', null=True)
    deftwopoint = TextField(column_name='DefTwoPoint', null=True)
    defensiveteam = TextField(column_name='DefensiveTeam', null=True)
    drive = TextField(column_name='Drive', null=True)
    epa = TextField(column_name='EPA', null=True)
    expointresult = TextField(column_name='ExPointResult', null=True)
    expoint_prob = TextField(column_name='ExPoint_Prob', null=True)
    exppts = TextField(column_name='ExpPts', null=True)
    fieldgoaldistance = TextField(column_name='FieldGoalDistance', null=True)
    fieldgoalresult = TextField(column_name='FieldGoalResult', null=True)
    field_goal_prob = TextField(column_name='Field_Goal_Prob', null=True)
    firstdown = TextField(column_name='FirstDown', null=True)
    fumble = TextField(column_name='Fumble', null=True)
    gameid = TextField(column_name='GameID', null=True)
    game_date = DateField(column_name='Game_Date', null=True)
    goaltogo = TextField(column_name='GoalToGo', null=True)
    hometeam = TextField(column_name='HomeTeam', null=True)
    hometimeouts_remaining_post = TextField(column_name='HomeTimeouts_Remaining_Post', null=True)
    hometimeouts_remaining_pre = TextField(column_name='HomeTimeouts_Remaining_Pre', null=True)
    home_wp_post = TextField(column_name='Home_WP_post', null=True)
    home_wp_pre = TextField(column_name='Home_WP_pre', null=True)
    interceptionthrown = TextField(column_name='InterceptionThrown', null=True)
    interceptor = TextField(column_name='Interceptor', null=True)
    no_score_prob = TextField(column_name='No_Score_Prob', null=True)
    onsidekick = TextField(column_name='Onsidekick', null=True)
    opp_field_goal_prob = TextField(column_name='Opp_Field_Goal_Prob', null=True)
    opp_safety_prob = TextField(column_name='Opp_Safety_Prob', null=True)
    opp_touchdown_prob = TextField(column_name='Opp_Touchdown_Prob', null=True)
    passattempt = TextField(column_name='PassAttempt', null=True)
    passlength = TextField(column_name='PassLength', null=True)
    passlocation = TextField(column_name='PassLocation', null=True)
    passoutcome = TextField(column_name='PassOutcome', null=True)
    passer = TextField(column_name='Passer', null=True)
    passer_id = TextField(column_name='Passer_ID', null=True)
    penalizedplayer = TextField(column_name='PenalizedPlayer', null=True)
    penalizedteam = TextField(column_name='PenalizedTeam', null=True)
    penaltytype = TextField(column_name='PenaltyType', null=True)
    penalty_yards = TextField(column_name='Penalty_Yards', null=True)
    playattempted = TextField(column_name='PlayAttempted', null=True)
    playtimediff = TextField(column_name='PlayTimeDiff', null=True)
    playtype = TextField(column_name='PlayType', null=True)
    posteamscore = TextField(column_name='PosTeamScore', null=True)
    puntresult = TextField(column_name='PuntResult', null=True)
    qbhit = TextField(column_name='QBHit', null=True)
    recfumbplayer = TextField(column_name='RecFumbPlayer', null=True)
    recfumbteam = TextField(column_name='RecFumbTeam', null=True)
    receiver = TextField(column_name='Receiver', null=True)
    receiver_id = TextField(column_name='Receiver_ID', null=True)
    reception = TextField(column_name='Reception', null=True)
    returnresult = TextField(column_name='ReturnResult', null=True)
    returner = TextField(column_name='Returner', null=True)
    rungap = TextField(column_name='RunGap', null=True)
    runlocation = TextField(column_name='RunLocation', null=True)
    rushattempt = TextField(column_name='RushAttempt', null=True)
    rusher = TextField(column_name='Rusher', null=True)
    rusher_id = TextField(column_name='Rusher_ID', null=True)
    sack = TextField(column_name='Sack', null=True)
    safety = TextField(column_name='Safety', null=True)
    safety_prob = TextField(column_name='Safety_Prob', null=True)
    scorediff = TextField(column_name='ScoreDiff', null=True)
    season = TextField(column_name='Season', null=True)
    sideoffield = TextField(column_name='SideofField', null=True)
    tackler1 = TextField(column_name='Tackler1', null=True)
    tackler2 = TextField(column_name='Tackler2', null=True)
    timesecs = IntegerField(column_name='TimeSecs', null=True)
    timeunder = TextField(column_name='TimeUnder', null=True)
    timeout_indicator = TextField(column_name='Timeout_Indicator', null=True)
    timeout_team = TextField(column_name='Timeout_Team', null=True)
    touchdown = TextField(column_name='Touchdown', null=True)
    touchdown_prob = TextField(column_name='Touchdown_Prob', null=True)
    twopointconv = TextField(column_name='TwoPointConv', null=True)
    twopoint_prob = TextField(column_name='TwoPoint_Prob', null=True)
    wpa = TextField(column_name='WPA', null=True)
    win_prob = TextField(column_name='Win_Prob', null=True)
    yardsaftercatch = TextField(column_name='YardsAfterCatch', null=True)
    yards_gained = TextField(column_name='Yards_Gained', null=True)
    airepa = TextField(column_name='airEPA', null=True)
    airwpa = TextField(column_name='airWPA', null=True)
    desc = TextField(null=True)
    down = TextField(null=True)
    game_time = TextField(null=True)
    posteam = TextField(null=True)
    posteam_timeouts_pre = TextField(null=True)
    qtr = IntegerField(null=True)
    sp = TextField(null=True)
    yacepa = TextField(column_name='yacEPA', null=True)
    yacwpa = TextField(column_name='yacWPA', null=True)
    ydsnet = TextField(null=True)
    ydstogo = TextField(null=True)
    yrdline100 = TextField(null=True)
    yrdln = TextField(null=True)

    class Meta:
        table_name = 'nflpbp'
        primary_key = False

    def to_dict(self):
        return {
        'gameid':self.gameid,
        'hometeam':self.hometeam,
        'qtr':self.qtr,
        'game_time':self.game_time,
        'timesecs':self.timesecs,
        'posteam':self.posteam,
        'defensiveteam':self.defensiveteam,
        'playtype':self.playtype,
        'desc':self.desc,
        'sideoffield':self.sideoffield,
        'yards_gained':self.yards_gained,
        'yrdln':self.yrdln,
        'ydstogo':self.ydstogo,
        }