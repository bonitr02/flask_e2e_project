from flask import Flask, render_template
import pandas as pd
import geopandas as gpd

app = Flask(__name__)

#@app.route('/')
#def home():
#    return f'Testing'

df = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/clean_drugsummary.csv')
merged_map = pd.read_csv('/home/rianne_bonitto/flask_e2e_project/data/drug_spendingclean_geolocation.csv')


@app.route('/')
def index(data=df):
    data = data.sample(30)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8000
        )
