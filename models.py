import mongoengine as me

class Play(me.Document):
  gid = me.StringField(max_length=16, required=True)
  date = me.DateTimeField(required=True)
  description = me.StringField(max_length=1024)
  offence_team = me.StringField(max_length=3)
  defence_team = me.StringField(max_length=3)
  offence_score = me.IntField(required=True)
  defence_score = me.IntField(required=True)
  week = me.IntField(required=True)
  quarter = me.IntField(required=True)
  minute = me.IntField(required=True)
  second = me.IntField(required=True)
  down = me.IntField()
  togo = me.IntField()
  yardline = me.IntField()
  season = me.IntField(required=True)
  playoffs = me.BooleanField(default=False)
  formation = me.StringField(max_length=16)
  turnover = me.StringField(max_length=16)
  yardage = me.IntField()
  action = me.StringField(max_length=16)
  success = me.BooleanField()
  points = me.IntField(default=0)
  penalty = me.BooleanField()
  key = me.StringField(max_length=128)
  meta = {'collection': 'play','indexes':['key']}

class Team(me.Document):
  meta = {'collection': 'team'}
  name = me.StringField(max_length=3)

  def __unicode__(self):
    return self.name
