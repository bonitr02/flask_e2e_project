import pandas as pd
import json
import re
# pip install fuzzywuzzy
from fuzzywuzzy import process, fuzz
import geopandas as gpd


#------------------ import drug ndc json file --------------
# json raw file download link: https://open.fda.gov/apis/drug/ndc/download/

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

merged.dtypes

# clean row names
merged['Tot_Prscrbrs'] = merged['Tot_Prscrbrs'].str.replace('[,]', '')
merged['Tot_Opioid_Prscrbrs'] = merged['Tot_Opioid_Prscrbrs'].str.replace('[,]', '')
merged['Tot_Opioid_Clms'] = merged['Tot_Opioid_Clms'].str.replace('[,]', '')
merged['Tot_Clms'] = merged['Tot_Clms'].str.replace('[,]', '')
merged['Opioid_Prscrbng_Rate'] = merged['Opioid_Prscrbng_Rate'].str.replace('[%]', '')

# convert string to int/float
merged['Tot_Prscrbrs'] = merged['Tot_Prscrbrs'].astype(int)
merged['Tot_Opioid_Clms'] = merged['Tot_Opioid_Clms'].astype(float)
merged['Tot_Opioid_Prscrbrs'] = merged['Tot_Opioid_Prscrbrs'].astype(int)
merged['Tot_Clms'] = merged['Tot_Clms'].astype(int)
merged['Opioid_Prscrbng_Rate'] = merged['Opioid_Prscrbng_Rate'].astype(float)

#export to csv
merged.to_csv('/data/drug_spendingclean_geolocation.csv')

merged_map = merged
merged_map[['Opioid_Prscrbng_Rate', 'geometry']].sort_values(by=['Opioid_Prscrbng_Rate'], ascending=False)
for x in merged_map.index:
  if merged_map.loc[x, "geometry"] == 'none' or merged_map.loc[x, "Opioid_Prscrbng_Rate"] == 'none':
    merged_map.drop(x, inplace = True)

merged_map.dropna(inplace=True)

gdf = gpd.GeoDataFrame(merged_map, geometry='geometry')

gdf.plot('Opioid_Prscrbng_Rate', legend=True)