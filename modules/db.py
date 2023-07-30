import mysql.connector

def connect(os):
  conn = mysql.connector.connect(
    host=os.environ['HOST'],
    user=os.environ['USER'],
    password=os.environ['PASSWORD'],
    database=os.environ['DATABASE'],
  )

  return conn