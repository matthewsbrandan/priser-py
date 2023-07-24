# region INTI
from collections import OrderedDict
import mysql.connector
import pandas as pd
import os
import sys

from dotenv import load_dotenv
load_dotenv()

conn = mysql.connector.connect(
  host=os.environ['HOST'],
  user=os.environ['USER'],
  password=os.environ['PASSWORD'],
  database=os.environ['DATABASE'],
)

cursor = conn.cursor()

SHOW_DETAILS = False

def loadDatas(datas: list, columns: list, caption: str):
  if(SHOW_DETAILS and caption):
    df = pd.DataFrame(datas, columns=columns)
    print(caption)
    print(df)
    print('\n\n')

  if(not datas): 
    return []
  
  parsed = []
  for data in datas:
    row = {}
    for i,cel in enumerate(data):      
      row[columns[i]] = cel
    parsed.append(row)
  return parsed
# endregion INTI

# region LOAD DAYS TO GENERATE SCALE
makeScales = [
  { 'date': '2023-07-25', 'weekday': 'tuesday',  'hour': '19:45', 'theme': 'Culto do fortalecimento' },
  { 'date': '2023-07-27', 'weekday': 'thursday', 'hour': '19:45', 'theme': 'Culto de cura e libertação' },
  { 'date': '2023-07-30', 'weekday': 'sunday',   'hour': '18:00', 'theme': 'Culto da família' },
]

makeScales.sort(key=lambda x: x['date'])

if(len(makeScales) == 0):
  print('-- É necessário indicar no mínimo uma escala para ser gerada')
  sys.exit()

if(SHOW_DETAILS):
  df = pd.DataFrame(makeScales, columns=makeScales[0].keys())
  print('SCALES TO MAKE ===================')
  print(df)

  print('\n\n')

ministry_id = 1
# endregion LOAD DAYS TO GENERATE SCALE

# region LOAD BACKGROUND DATAS
query = "SELECT `id`, `name`, `slug` FROM `abilities`"
cursor.execute(query)
abilities = loadDatas(cursor.fetchall(), cursor.column_names, 'ABILITIES ===================')

query = f"""
  SELECT
    um.id,
    um.nickname,
    u.availability,
    GROUP_CONCAT(ua.ability_id SEPARATOR ',') AS abilities
  FROM
    user_ministries um
  LEFT JOIN
    user_abilities ua ON um.id = ua.user_ministry_id
  INNER JOIN
    users u ON um.user_id = u.id
  WHERE
    um.ministry_id = {ministry_id}
  GROUP BY
    um.id,
    um.nickname
"""

cursor.execute(query)
integrants = loadDatas(cursor.fetchall(), cursor.column_names, 'INTEGRANTS ===================')

integrantsByAbility = {}
for integrant in integrants:
  if(not integrant['abilities']):
    continue
  integrant_ab = integrant['abilities'].split(',')
  for ab in integrant_ab:
    findedAbility = next(filter(lambda ability: str(ability['id']) == ab, abilities), None)

    if(not findedAbility):
      continue

    ab_slug = findedAbility['slug']
    if(ab_slug in integrantsByAbility):
      integrantsByAbility[ab_slug].append(integrant)
    else:
      integrantsByAbility[ab_slug] = [integrant]

firstDate = makeScales[0]['date']

query = f"""
  SELECT * FROM
    `scales` `s`
  INNER JOIN
    `scale_users` `su`
  ON
    `s`.`id` = `su`.`scale_id`
  WHERE
    `ministry_id` = {ministry_id} AND
    `s`.`published` = 1 AND
    `date` BETWEEN DATE_SUB('{firstDate}', INTERVAL 2 MONTH) AND '{firstDate}' 
  ORDER BY
    `s`.`date` DESC
"""
cursor.execute(query)

scales = loadDatas(cursor.fetchall(), cursor.column_names, 'PREV-SCALES =================')
# endregion LOAD BACKGROUND DATAS

ministers = integrantsByAbility['ministro']

# region SEGMENTATION BY DAY OF THE WEEK
weekdays = list(OrderedDict.fromkeys(map(lambda scale: scale['weekday'], makeScales)))
availableMinistersToWeekday = {}
scalesOnAvailableDays = {}
ministersQueue = {}
for weekday in weekdays:
  scalesOnAvailableDays[weekday] = list(filter(lambda scale: weekday in scale['weekday'], scales))
  for minister in filter(lambda scale: 'ministro' in scale['ability'].split(','), scalesOnAvailableDays[weekday]):
    if(weekday in ministersQueue):
      if(not minister['nickname'] in ministersQueue[weekday]):
        ministersQueue[weekday].append(minister['nickname'])
    else:
      ministersQueue[weekday] = [minister['nickname']]
  
  availableMinistersToWeekday[weekday] = list(
    map(lambda minister: minister['nickname'], filter(lambda minister: weekday in minister['availability'].split(','), ministers))
  )
  for available in availableMinistersToWeekday[weekday]:
    if(weekday in ministersQueue):
      if(not available in ministersQueue[weekday]):
        ministersQueue[weekday].append(available)
    else:
      ministersQueue[weekday] = [available]
# endregion SEGMENTATION BY DAY OF THE WEEK

# region CREATING SCALES
for scale in makeScales:
  nextMinister = ministersQueue[scale['weekday']].pop()
  ministersQueue[scale['weekday']].insert(0, nextMinister)

  scale['integrants'] = {
    'ministro': nextMinister,
  }
# endregion CREATING SCALES
  
# region HELPER TO SHOW
show = makeScales
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
# endregion HELPER TO SHOW

cursor.close()
conn.close()