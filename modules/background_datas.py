import pandas as pd

def loadDatas(datas: list, columns: list, caption: str, SHOW_DETAILS):
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

def load(cursor, ministry_id, makeScales, SHOW_DETAILS):
  query = "SELECT `id`, `name`, `slug` FROM `abilities`"
  cursor.execute(query)
  abilities = loadDatas(cursor.fetchall(), cursor.column_names, 'ABILITIES ===================', SHOW_DETAILS=SHOW_DETAILS)

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
    AND
      um.nickname IS NOT NULL
    GROUP BY
      um.id,
      um.nickname
  """

  cursor.execute(query)
  integrants = loadDatas(cursor.fetchall(), cursor.column_names, 'INTEGRANTS ===================', SHOW_DETAILS=SHOW_DETAILS)

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

  scales = loadDatas(cursor.fetchall(), cursor.column_names, 'PREV-SCALES =================', SHOW_DETAILS=SHOW_DETAILS)
  
  return [scales, integrantsByAbility]