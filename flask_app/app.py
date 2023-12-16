from flask import Flask, render_template, request, jsonify
import pandas as pd
import geopandas as gpd
import json
import requests
import matplotlib.pyplot as plt
import io
import base64

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


#@app.route('/')
#def home():
#    return render_template('index.html', data=df)

#states= merged_map['state'], data value= merged_map['Opioid_Prscrbng_Rate']
@app.route('/', methods=['GET', 'POST'])
def index():
    #states = sorted(merged_map['state'].unique())
    states = merged_map['state'].unique()
    #states = sorted(merged_map['state'])

    selected_state = request.form.get('state') or states[0]
    img = create_plot(selected_state)

    return render_template("index.html", states=states, selected_state=selected_state, img=img)

def create_plot(state):
    #rate = merged_map[merged_map['Opioid_Prscrbng_Rate'] == state ]
    #selected_state_avg = df_teeth[df_teeth['StateDesc'] == state]['Data_Value'].mean()

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