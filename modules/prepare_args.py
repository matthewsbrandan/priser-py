from datetime import datetime, timedelta
import argparse
import sys
import json
import pandas as pd
import math

def ask_confirmation(prompt, retry_limit=3):
  response = input(prompt + " [y/n]: ").lower()
  if response == "y":
    return True
  elif response == "n":
    return False
  else:
    if retry_limit > 1:
      print("Resposta inválida. Digite 'y' para sim ou 'n' para não.")
      return ask_confirmation(prompt, retry_limit - 1)
    else:
      print("Três tentativas inválidas consecutivas. Encerrando a aplicação.")
      exit(1)

def get_next_tuesday():
  today = datetime.today()
  days_until_tuesday = (1 - today.weekday() + 7) % 7
  next_tuesday = today + timedelta(days=days_until_tuesday)
  return next_tuesday

def get_weekday_occurrence(day):
  return math.floor(day/7) + 1

def requested_scales(os):
  # { 
  #   "tuesday": string,
  #   "thursday": string,
  #   "sunday": {
  #     "first": string,
  #     "third": string,
  #     "default": string,
  #   },
  #   "msunday": string
  # }  
  themeByWeekday = json.loads(os.environ['THEME_BY_WEEKDAY'])
  hourByWeekday = json.loads(os.environ['HOUR_BY_WEEKDAY'])

  parser = argparse.ArgumentParser(
    prog='Praiser Automation',
    description='This program analyzes scale history and generates a scale for selected days'
  )

  parser.add_argument('-d', '--days', type=str, help='Days you want to generate scales, separated by a comma. Exemple: "DD-MM,DD-MM" or "DD-MM-YY, ..."')
  parser.add_argument('-w', '--week', nargs='?', const='tuesday,thursday,sunday', help='Generate scales for the week. If you do not inform the dats of the week, it will generate for "tuesday,thursday,sunday". Note: msunday for sunday morning')
  parser.add_argument('-m', '--month', nargs='?', const='n', help='It will generate scales until the end of the month, on Tuesdays, Thursdays and Sundays (first Sunday 2 services). If you want to add other days, enter the date after -m="18-10,23-10" these days will be included in the final date')
  parser.add_argument('-r','--raw', type=str, help='Type all details: date(d:),hour(h:),theme(t:). Example "d:20-12h:19:30t:Holy Supper,d:25-12h:22:00t:Christmas"')

  args = parser.parse_args()

  makeScales = []

  if(args.days):
    print('Handle days in development')
    sys.exit()
  elif(args.week):
    if(args.week != 'tuesday,thursday,sunday'):
      print('O sistema ainda não possui suporte para dias da semana explícitos')
      sys.exit()

    days = []
    tuesday = get_next_tuesday()
    days.append([tuesday, 'tuesday'])
    days.append([tuesday + timedelta(days=2), 'thursday'])
    days.append([tuesday + timedelta(days=2+3), 'sunday'])

    for day in days:
      if(day[1] == 'sunday'):
        occurrence = get_weekday_occurrence(int(day[0].strftime('%d')))
        defaultTheme = themeByWeekday['sunday']['default'] or 'Culto'
        if(occurrence == 1):
          makeScales.append({
            'date': day[0].strftime('%Y-%m-%d'),
            'weekday': day[1],
            'hour': hourByWeekday['msunday'],
            'theme': themeByWeekday['msunday'] or 'Culto',
          })
          
          theme = themeByWeekday['sunday']['first'] or defaultTheme
        elif(occurrence == 3):
          theme = themeByWeekday['sunday']['third'] or defaultTheme
        else:
          theme = defaultTheme
      else:
        theme = themeByWeekday[day[1]] or 'Culto'

      makeScales.append({
        'date': day[0].strftime('%Y-%m-%d'),
        'weekday': day[1],
        'hour': hourByWeekday[day[1]],
        'theme': theme,
      })
  elif(args.month):
    print('Handle month in development')
    sys.exit()
  elif(args.raw):
    print('Handle raw in development')
    sys.exit()
  else:
    print('-- É necessário indicar no mínimo uma escala para ser gerada.\n[Digite ./main -h para ter mais detalhes]')
    sys.exit()

  makeScales.sort(key=lambda x: x['date'])

  if(len(makeScales) == 0):
    print('-- É necessário indicar no mínimo uma escala para ser gerada')
    sys.exit()
  
  df = pd.DataFrame(makeScales, columns=makeScales[0].keys())
  print('SCALES TO MAKE ===================')
  print(df)

  print('\n\n')

  if not ask_confirmation('Deseja confirmar a geração automática para os dias selecionados?'):
    sys.exit()
    
  return makeScales