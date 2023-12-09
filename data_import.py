import pandas as pd
import json
import re
# pip install fuzzywuzzy
from fuzzywuzzy import process, fuzz
import geopandas as gpd


#------------------ import drug ndc json file --------------
# json file download link: https://open.fda.gov/apis/drug/ndc/download/
# import json file
data = json.load(open('/data/drugs.json'))
js_df = pd.DataFrame(data['results'])
# convert to csv and export
js_df.to_csv('data/drugs_df.csv')

#import new csv
js_df2 = pd.read_csv('/data/drugs_df.csv', index_col=0)

#drop unwanted columns
newdf = js_df2.drop(columns=['finished','packaging','listing_expiration_date','openfda','marketing_category','spl_id','product_type','marketing_start_date','product_id','application_number','active_ingredients', 'pharm_class','marketing_end_date','brand_name_suffix'])
# remove special characters
newdf = newdf.apply(lambda x: x.str.replace('[^\w\s]', ''))
# export cleaned dataframe
newdf.to_csv('/data/clean_drugsummary.csv')

#------------------ Import geospatial and Medicare Opioid Prescribing rates ---------
df_spatial = gpd.read_file('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json')

df_op = pd.read_csv('/content/Medicare_Part_D_Opioid_Prescribing_Rates_by_Geography_2021.csv')

#rename columns to state
op_state = df_op.rename(columns={"Prscrbr_Geo_Desc":"state"})
spat_state = df_spatial.rename(columns={"name":"state"})

op_state.sample(5)
spat_state.sample(5)

## function to get best match
def get_best_match(name, choices, threshold=90):
    match_data = process.extractOne(name, choices)
    if match_data:
        match, score, _ = match_data  # Unpack three elements, ignoring the index
        return match if score >= threshold else None
    return None

## apply fuzzy matching
op_state['state'] = op_state['state'].apply(lambda x: get_best_match(x, spat_state['state']))

## merge the dataframes based on the matched names
merged = pd.merge(op_state, spat_state, left_on='state', right_on='state', how='left')

#drop empty
merged.dropna()
merged.dropna(subset=['geometry'])
len(merged)

#export to csv
merged.to_csv('/data/drug_spending_geolocation.csv')