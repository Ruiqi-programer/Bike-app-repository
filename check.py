import pymysql
import pandas as pd

conn = pymysql.connect(
    host="localhost",  
    user="root",
    password="656692",
    database="dublinbikesystem"
)


df = pd.read_sql("SELECT * FROM station", conn)
print(df.head()) 
conn.close()