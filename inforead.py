from models import Play
import csv
from mongoengine import connect
import pdb, traceback, sys
import datetime

connect('nfl')

def next_tuesday(d):
    weekday = 1 #Tuesday!
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def parse_description(des):
  '''
  want to return formation, turnover, yardage, action, success ,points, penalty
  '''
  formation=None
  turnover=None
  yardage=None
  action=None
  success=None
  points=0
  penalty=False

  splitdes = des[:-1].lower().split(' ') #don't need trailing period
  if 'punts' in splitdes:
    formation = 'punt'
  elif 'kicks' in splitdes:
    formation = 'kickoff'
    if 'touchback' in splitdes: #I guess this is a success for kickoff...
      success=True
    else:
      success=False
  elif 'field' in splitdes or 'extra' in splitdes:
    formation = 'kick'
    if 'good' in splitdes:
      success=True
      if 'field' in splitdes:
        points = 3
      else:
        points = 1
    else:
      success=False
  else:
    #here we want k
    if '(shotgun)' in splitdes:
      formation = 'shotgun'
    else:
      formation = 'undercenter'
    #deal with yardage and action
    if 'pass' in splitdes:
      action='pass'
    elif [i for i in ['up', 'left', 'right'] if i in splitdes]:
      action='run'
    try:
      forind = splitdes.index('for')
      yardage = int(splitdes[forind+1])
    except ValueError: #both value errors...
      yardage = 0

  if 'fumble' in splitdes:
    turneover = 'fumble'
    #still keep in for initial yardage
  elif 'intercepted' in splitdes:
    turnover = 'intercepted'
    yardage=None #nothing gained for the offense

  if 'touchdown' in splitdes:
    points = 6

  if 'penalty' in splitdes:
    penalty=True

  return (formation,turnover,yardage,action, success, points, penalty)

def read_data(csvfile):
  with open(csvfile, 'rU') as f:
    next(f)
    reader = csv.reader(f)
    week = 0 #this is for the week number of the season
    week_cutoff = None
    for row in reader:
      if all([r == '' for r in row]):
        break
      gid = row[0]
      #we can get the date now
      date = datetime.datetime.strptime(gid[0:8],'%Y%m%d')
      #now we want to deal with the week number
      if week_cutoff != next_tuesday(date):
        week += 1
        week_cutoff = next_tuesday(date)
        print 'season ' + csvfile[5:9] + ': Week ' + str(week)
      qtr = int(row[1])
      #need to deal with kickoff, should be 60 if both are 0
      #also play under review...
      row3errors = set(['.M', '**', 'ND','.O','.B','.H','.W','.G'])
      if row[3] in row3errors:
        #play under review...
        minute = 0
        second = 0
      else:
        minute = int(row[2]) if row[2] else 0
        second = int(row[3]) if minute and row[3] else 0
      off_team = row[4]
      def_team = row[5]
      down_num = int(row[6]) if row[6] else -1
      togo = int(row[7]) if row[7] else -1
      yardline = int(row[8]) if row[8] else -1
      description = row[9]
      if description and description[0] == '\xa0':
        description =''
      offscore = int(row[10]) if row[10] else 0
      defscore = int(row[11]) if row[11] else 0
      season = int(csvfile[5:9])
      playoffs = True if week > 16 else False #things greater than week 16 are playoffs
      formation, turnover, yardage, action, success, points, penalty = parse_description(description)
      key_rows = [0,1,2,3,6,7,8,10,11]
      key = ''.join([row[ind] for ind in key_rows])
      plays = Play.objects.filter(key=key)
      #now we want to get the info
      if not plays or all([p.description == description for p in plays]):
        play = Play(gid=gid,
                    date=date,
                    description=description,
                    offence_team=off_team,
                    defence_team=def_team,
                    offence_score=offscore,
                    defence_score=defscore,
                    week=week,
                    quarter=qtr,
                    minute = minute,
                    second = second,
                    down = down_num,
                    togo = togo,
                    yardline = yardline,
                    season = season,
                    playoffs = playoffs,
                    formation = formation,
                    turnover = turnover,
                    yardage = yardage,
                    action = action,
                    success = success,
                    points = points,
                    penalty = penalty,
                    key = key,
                    )
        play.save()

if __name__ == '__main__':
  #import os
  #files = os.listdir('data')
  #for f in files:
  try:
    read_data('data/2012_nfl_pbp_data.csv')
  except:
    type, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)
