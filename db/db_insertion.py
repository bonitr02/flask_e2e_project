import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
import numpy as np
from dotenv import load_dotenv
from pandas import read_sql
import os

load_dotenv('/home/rianne_bonitto/flask_e2e_project/.env')

# Database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

# Connect to the database
connectionString = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

# Test connection
engine = create_engine(connectionString)
connection = engine.connect()

# Try and read tables data from the database
tables = pd.read_sql("SHOW TABLES", connection)

# Import cleaned drug database
df = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/clean_drugsummary.csv')

## send df to drugs table
df.to_sql('drugs', con=connection, if_exists='append', index=False)

## test drugs table again
test_drugs = pd.read_sql("SELECT * FROM drugs", connection)
print(test_drugs)

#test data insertion
pd.read_sql("SELECT * FROM drugs LIMIT 5;", engine)

connection.close()