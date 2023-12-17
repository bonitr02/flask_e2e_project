import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
import numpy as np
from dotenv import load_dotenv
from pandas import read_sql
import os

load_dotenv('.env')

# Database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

# Connect to the database
connectionString = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

# Configure engine
engine = create_engine(connectionString)
connection = engine.connect()

# Try and read tables data from the database
tables = pd.read_sql("SHOW TABLES", connection)

# Import cleaned drug database
df = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/clean_drugsummary.csv')
len(df) #134369
df1 = df.drop(df.columns[[0]], axis=1)
len(df1) #134369
df2 = df1[df1['generic_name'].str.len() <= 50]
len(df2) #125505
df3 = df2[df2['brand_name_base'].str.len() <= 50]
len(df3) #102071
df4 = df3[df3['labeler_name'].str.len() <= 50]
len(df4) #101075
## send df to drugs table
df4.to_sql('drugs1', con=connection, if_exists='replace', index=False)

## test drugs table
test_drugs = pd.read_sql("SELECT * FROM drugs", connection)
print(test_drugs)

#test data insertion
test2 = pd.read_sql("SELECT * FROM drugs LIMIT 5;", engine)

connection.close()