import mysql.connector
import pandas as pd
import os

from dotenv import load_dotenv
load_dotenv()

conn = mysql.connector.connect(
  host=os.environ['HOST'],
  user=os.environ['USER'],
  password=os.environ['PASSWORD'],
  database=os.environ['DATABASE'],
)

cursor = conn.cursor()

ministry_id = 1

query = f'SELECT `su`.`scale_id`, `s`.`date`, `s`.`weekday`, `s`.`hour`, `su`.`ability`, `su`.`nickname`, `su`.`user_id` FROM `scales` `s` INNER JOIN `scale_users` `su` ON  `s`.`id` = `su`.`scale_id` WHERE `s`.`published` = 1 AND `ministry_id` = {ministry_id} ORDER BY `s`.`id` DESC LIMIT 10;'

cursor.execute(query)
last10Scales = cursor.fetchall()

df = pd.DataFrame(last10Scales, columns=cursor.column_names)

print(df)

cursor.close()
conn.close()