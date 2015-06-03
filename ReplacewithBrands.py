import pandas as pd
import nltk
import string
from collections import OrderedDict

# Read in models/brands to search and replace
xls = pd.ExcelFile('Cars_make_model.xlsm')
models_df = xls.parse('Models', skiprows=3, encoding='utf-8')
del models_df['Unnamed: 0']

# Read in Edmunds data
edmunds = pd.read_csv('Edmunds.csv')
del edmunds['Unnamed: 0']

# Prepare models/brands for replacement and convert data into printable strings (to avoid errors)
brands = models_df['Replace'].tolist()
models = models_df['Search'].tolist()
comments = edmunds['Comments'].tolist()

brands = [filter(lambda x: x in string.printable, brands[i]) for i in range(len(brands))]
models = [filter(lambda x: x in string.printable, models[i]) for i in range(len(models))]
comments = [filter(lambda x: x in string.printable, str(comments[i])) for i in range(len(comments))]

edmunds['Comments'] = comments

# Change commonly seen '3 series' to 'bmw'
edmunds = edmunds.apply(lambda x: x.str.replace('3 series', 'bmw',case=False))

# Change all models seen in "Search" field with brands in "Replace" field
for i in range(len(models)):
    edmunds = edmunds.apply(lambda x: x.str.replace(models[i],brands[i], case=False))

# Read in data from sheet 2 for replacing plural brands with singular
models_plur_df = xls.parse('Models (Plural and Multiple)',skiprows=3)
del models_plur_df['Unnamed: 0']

plur_models = models_plur_df['Search'].tolist()
plur_brands = models_plur_df['Replace'].tolist()

plur_brands = [filter(lambda x: x in string.printable, str(plur_brands[i])) for i in range(len(plur_brands))]
plur_models = [filter(lambda x: x in string.printable, str(plur_models[i])) for i in range(len(plur_models))]

# Replace plural brands with singular
for i in range(len(plur_models)):
    edmunds = edmunds.apply(lambda x: x.str.replace(plur_models[i],plur_brands[i], case=False))

# WRITE TEMP TO CSV - only models changed
edmunds.to_csv('only_models.csv')

# READ IN only_models csv if needed
# edmunds = pd.read_csv('Replaced_Steps/only_models.csv')


# Frequency counts for brands            
brand_counts = {}
for brand in brands:
    brand = brand.lower()
    brand_counts[brand] = 0
    for comment in edmunds['Comments']:
        if brand in comment.lower():
            brand_counts[brand] += 1
            
# Top 20 brands
top20brands = sorted(brand_counts.items(), key=lambda (k,v): v, reverse=True)[:20]
top20brands

# Build list of top 10 brands - ensuring only real brands in top 10
not_brands = ['car','sedan','seat','problem']
top10brands = []
for i in top20brands:
    if i[0] not in not_brands and len(top10brands) < 10:
        top10brands.append(i)
top10brands = dict(top10brands)

# Read in data from sheet 3 to replace attributes, clear printable error
attributes_df = xls.parse('Attributes',skiprows=3)
del attributes_df['Unnamed: 0']
attributes_df_new = attributes_df.ix[0:len(attributes_df)-3]

attr_orig = attributes_df_new['Search'].tolist()
attr_replace = attributes_df_new['Replace'].tolist()

attr_orig = [filter(lambda x: x in string.printable, str(attr_orig[i])) for i in range(len(attr_orig))]
attr_replace = [filter(lambda x: x in string.printable, str(attr_replace[i])) for i in range(len(attr_replace))]

# Replace attributes
for i in range(len(attr_orig)):
    edmunds = edmunds.apply(lambda x: x.str.replace(attr_orig[i],attr_replace[i], case=False))

# Write temp csv with models and attributes
edmunds.to_csv('Replaced_Steps/models_attributes.csv')

# Read in models_attributes csv if needed
# edmunds = pd.read_csv('Replaced_Steps/models_attributes.csv')

# Count frequency of attributes mentioned
attributes = set(attributes_df_new['Replace'])
edmunds['Comments'] = edmunds['Comments'].str.lower()

attribute_counts = {}
for attr in attributes:
    attribute_counts[attr] = 0
    for comment in edmunds['Comments']:
        if attr in comment:
            attribute_counts[attr] += 1

# Top 5 most mentioned attributes
top5attrs = sorted(attribute_counts.items(), key=lambda (k,v): v, reverse=True)[:5]

# Read in data from sheet 3 to replace phrases with "aspirational"
aspirational_df = xls.parse('Relacement for Aspirations',skiprows=3)
del aspirational_df['Unnamed: 0']
aspirational_df_new = aspirational_df.ix[0:len(aspirational_df)-3]

asp_orig = aspirational_df['Search'].tolist()
asp_replace = aspirational_df['Replace'].tolist()

asp_orig = [filter(lambda x: x in string.printable, str(asp_orig[i])) for i in range(len(asp_orig))]
asp_replace = [filter(lambda x: x in string.printable, str(asp_replace[i])) for i in range(len(asp_replace))]


# Replace phrases with aspirational
for i in range(len(asp_orig)):
    edmunds2 = edmunds2.apply(lambda x: x.str.replace(asp_orig[i],asp_replace[i], case=False))

# WRITE final csv with all replacements
edmunds2.to_csv('Replaced_Steps/everything_replaced.csv')

