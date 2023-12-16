from flask import Flask, render_template, request, jsonify
import pandas as pd
import geopandas as gpd
import json
import requests

app = Flask(__name__)

df = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/clean_drugsummary.csv')
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


@app.route('/')
def home():
    return render_template('index.html', data=df)

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8000
        )