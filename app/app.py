from flask import Flask, render_template, request, jsonify
import pandas as pd
import geopandas as gpd
import json
import requests
import matplotlib.pyplot as plt
import io
import base64
import os
from sqlalchemy import create_engine, inspect, Column, Integer, String, Date, ForeignKey, text
from sqlalchemy.orm import relationship, Session, declarative_base
from dotenv import load_dotenv


load_dotenv('.env')  # Load environment variables from .env file

# Database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

# Connect to the database
connectionString = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    f"?charset={DB_CHARSET}"
)
'''
# Configure engine
engine = create_engine(connectionString, echo=False)
connection = engine.connect()

# Try and read tables data from the database
tables = pd.read_sql("SHOW TABLES", engine)
print(tables)
test2 = pd.read_sql("SELECT * FROM drugs LIMIT 5;", engine)
print(test2)

#Import sql drug database

drug_db = pd.read_sql("SELECT * FROM drugs;", engine)
print(drug_db)

drug_db.to_csv('/home/rianne_bonitto/flask_e2e_project/data/mysql_drug_db.csv')

'''
app = Flask(__name__)

df = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/mysql_drug_db.csv')
merged_map = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/drug_spendingclean_geolocation.csv')

@app.route('/class', methods =['GET'])
def fda_search(): 
    class1 = request.args.get('class', "Please enter value again") 
    search = 'https://api.fda.gov/drug/ndc.json?search=dea_schedule:'
    responses = []
    
    key = search + class1 + '&limit=100'
    response1 = requests.get(key)
    responses.append(response1)
    
    r0 = responses [0]
    r0_json = r0.json()
    r0_results = r0_json['results']
  
    return jsonify(r0_results)


#@app.route('/')
#def home():
#    return render_template('index.html', data=df)

def data(data=df):
    data = data
    return render_template('index.html', data=data)

@app.route('/', methods=['GET', 'POST'])
def index():
    states = merged_map['state'].unique()
    selected_state = request.form.get('state') or states[0]
    img = create_plot(selected_state)

    return render_template("index.html", states=states, selected_state=selected_state, img=img)

def create_plot(state):
    overall_avg = merged_map['Opioid_Prscrbng_Rate'].mean()
    selected_state_avg = merged_map[merged_map['state'] == state]['Opioid_Prscrbng_Rate'].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(['Selected State', 'Overall Average'], [selected_state_avg, overall_avg], color=['cyan', 'aquamarine'])
    ax.axhline(selected_state_avg, color='gray', linestyle='dashed', alpha=0.7)
    ax.set_ylabel('Data Value (Age-adjusted prevalence) - Percent')
    ax.set_ylim(0, 10)
    ax.set_title('All Teeth Lost in NY, CA and FL by Age-adjusted PrevalenceComparison')
    
    # Convert plot to PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    return base64.b64encode(img.getvalue()).decode()

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8000
        )
