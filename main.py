# region INTI
from collections import OrderedDict
import pandas as pd
import json

from modules import prepare_args
from modules import db
from modules import integrants_queue
from modules import background_datas

#region HANDLE ENVIROMENT VARIABLES
from dotenv import load_dotenv
import os
load_dotenv()
#endregion HANDLE ENVIROMENT VARIABLES

SHOW_DETAILS = True

makeScales = prepare_args.requested_scales(os)

ministry_id = int(os.environ['MINISTRY_ID'])
pre_settings = json.loads(os.environ['PRE_SETTIGNS'])

conn = db.connect(os)

cursor = conn.cursor()

def show(show):
  if(show and len(show) > 0):
    if type(show) is list: 
      if type(show[0]) is dict: 
        df = pd.DataFrame(show, columns=show[0].keys())
        print(df)
      else:
        df = pd.DataFrame(show)
        print(df)
    elif type(show) is dict:    
      for key in show.keys():
        print(key, '--------------- \n')
        if type(show[key]) is list:
          if type(show[key][0]) is dict: 
            df = pd.DataFrame(show[key], columns=show[key][0].keys())
            print(df)
          else:
            df = pd.DataFrame(show[key])
            print(df)
        else:
          print(show[key])
        print('\n')
    
    print('\n\n')
# endregion INTI

[scales, integrantsByAbility] = background_datas.load(
  cursor=cursor,
  ministry_id=ministry_id,
  makeScales=makeScales,
  SHOW_DETAILS=SHOW_DETAILS,
)

# region SEGMENTATION BY DAY OF THE WEEK
weekdays = list(OrderedDict.fromkeys(map(lambda scale: scale['weekday'], makeScales)))
ministersQueue = integrants_queue.get_ministers_queue(
  weekdays=weekdays,
  ministers=integrantsByAbility['ministro'],
  scales=scales
)
musiciansQueue = []
backingsQueue = []
datashowsQueue = []
soundmansQueue = []
# endregion SEGMENTATION BY DAY OF THE WEEK

# region CREATING SCALES
for scale in makeScales:
  nextMinister = ministersQueue[scale['weekday']].pop()
  ministersQueue[scale['weekday']].insert(0, nextMinister)

  scale['integrants'] = {
    'ministro': nextMinister,
  }

  # if(pre_settings and pre_settings[scale['weekday']]):
  #   setting_weekday = pre_settings[scale['weekday']]
  #   if(setting_weekday['musicos']):
  #     for musician in setting_weekday['musicos']:

  

  
# endregion CREATING SCALES
cursor.close()
conn.close()