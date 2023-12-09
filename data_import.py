import pandas as pd
import json
import re

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