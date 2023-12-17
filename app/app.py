from flask import Flask, render_template, request, jsonify, url_for, redirect, session
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
import logging
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token

#Configure logger
logging.basicConfig(
    level=logging.DEBUG,
    filename="logs/app.log",
    filemode="w",
    format='%(levelname)s - %(name)s - %(message)s'
)

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
# Code to configure engine and import sql database. Code runs successfully one line at a time, but not when running the python app.py command #
# mysql database imported and converted to csv using pandas
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
# Import mysql drug database and drug spending geolocation database
df = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/mysql_drug_db.csv')
merged_map = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/drug_spendingclean_geolocation.csv')

# Configure google client 
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

app = Flask(__name__)
app.secret_key = os.urandom(12)
oauth = OAuth(app)


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/google/')
def google():
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    redirect_uri = url_for('google_auth', _external=True)
    print('REDIRECT URL: ', redirect_uri)
    session['nonce'] = generate_token()
    
    redirect_uri = "https://8000-cs-296425122942-default.cs-us-east1-vpcf.cloudshell.dev/google/auth/"
    return oauth.google.authorize_redirect(redirect_uri, nonce=session['nonce'])

@app.route('/google/auth/')
def google_auth():        
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token, nonce=session['nonce'])
    session['user'] = user
    return redirect('/index')

@app.route('/class', methods =['GET'])
def fda_search(): 
    try:
        class1 = request.args.get('class', "Please enter value again") 
        search = 'https://api.fda.gov/drug/ndc.json?search=dea_schedule:'
        responses = []
    
        key = search + class1 + '&limit=100'
        response1 = requests.get(key)
        responses.append(response1)
    
        r0 = responses [0]
        r0_json = r0.json()
        r0_results = r0_json['results']

        logging.debug("FDA drug information returned")
        return jsonify(r0_results)
    
    except Exception as e:
        logging.error(f"An error occurred! {e}")
        return "try again"

@app.route('/drugs')
def drugs(data=df):
    try:
        data = data.sample(30)
        
        logging.debug("Index page accessed")
   
        return render_template('drugs.html', data=data)
    
    except Exception as e:
        logging.error(f"An error occurred! {e}")
        return "try again"

@app.route('/index', methods=['GET', 'POST'])
def index():
    try:
        states = merged_map['state'].unique()
        selected_state = request.form.get('state') or states[0]
        img = create_plot(selected_state)
        
        logging.debug("Index page accessed")
        return render_template("index.html", states=states, selected_state=selected_state, img=img)
    
    except Exception as e:
        logging.error(f"An error occurred! {e}")
        return "try again"

def create_plot(state):
    try:
        overall_avg = merged_map['Opioid_Prscrbng_Rate'].mean()
        selected_state_avg = merged_map[merged_map['state'] == state]['Opioid_Prscrbng_Rate'].mean()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(['Selected State', 'National Average'], [selected_state_avg, overall_avg], color=['green', 'gray'])
        ax.axhline(selected_state_avg, color='gray', linestyle='dashed', alpha=0.7)
        ax.set_ylabel('% Prescribed')
        ax.set_ylim(0, 10)
        ax.set_title('% Controlled Medications Prescribed by State vs National (2021 Medicare Report)')
    
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        logging.debug("Plot created")
        return base64.b64encode(img.getvalue()).decode()
    
    except Exception as e:
        logging.error(f"An error occurred! {e}")
        return "try again"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8000
        )


