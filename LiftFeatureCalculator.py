from textblob import TextBlob
import pattern.en
import pandas as pd
import string


# Read in data with replaced brands and attributes
data = pd.read_csv("everything_replaced.csv")

# Read in brands sheet 
xls = pd.ExcelFile('Cars make model.xlsm')
models_df = xls.parse('Models', skiprows=3, encoding='utf-8')
del models_df['Unnamed: 0']

# Read in attributes sheet
attributes_df = xls.parse('Attributes',skiprows=3)
del attributes_df['Unnamed: 0']
attributes_df_new = attributes_df.ix[0:len(attributes_df)-3]

#Read in aspirational sheet
aspirations_df = xls.parse('Relacement for Aspirations',skiprows=3)
del aspirations_df['Unnamed: 0']
aspirations_df_new = attributes_df.ix[0:len(attributes_df)-2]

# Convert data into printable strings (to avoid errors)
brands = models_df['Replace'].tolist()
attr_replace = attributes_df['Replace'].tolist()
brands = [filter(lambda x: x in string.printable, brands[i]) for i in range(len(brands))]
attr_replace = [filter(lambda x: x in string.printable, str(attr_replace[i])) for i in range(len(attr_replace))]

# Frequency counts for brands            
brand_counts = {}
for brand in brands:
    brand = brand.lower()
    brand_counts[brand] = 0
    for comment in data['Comments']:
        if brand in comment.lower():
            brand_counts[brand] += 1
            
# Top 20 brands
top20brands = sorted(brand_counts.items(), key=lambda (k,v): v, reverse=True)[:20]
top20brands

# Build list of top 10 brands
not_brands = ['car','sedan','seat','problem']
top10brands = []
top5brands = []
for i in top20brands:
    if i[0] not in not_brands and len(top10brands) < 10:
        top10brands.append(i)
    if i[0] not in not_brands and len(top5brands) < 5:
        top5brands.append(i)
        
top10brands = dict(top10brands)
top5brands = dict(top5brands)

brandlist = top10brands.keys()

LiftMatrix = pd.DataFrame(0, index=brandlist, columns=brandlist)
ProbVector = []
data["Comments"] = data["Comments"].str.lower()

ProbDict = {}
for brand in brandlist:
	ProbDict[brand] = 0

for x in range(len(brandlist)):
	for y in data["Comments"]:
		if brandlist[x] in y:
			ProbDict[brandlist[x]] +=1

probs = pd.DataFrame([ProbDict])
probs = probs.transpose()
probs = probs.apply(lambda x: x/len(data))

for x in brandlist:
	for y in brandlist:
		for z in data["Comments"]:
			if x in z and y in z:
				LiftMatrix[x][y] += 1
			if x == y:
				LiftMatrix[x][y] = 0

LiftMatrix = LiftMatrix.apply(lambda x: x/len(data))
FinalLift = pd.DataFrame(0.0, index=brandlist, columns=brandlist)

for x in brandlist:
	for y in brandlist:
		FinalLift[x][y] = float(LiftMatrix[x][y]) / float((probs[0][x]) * (probs[0][y])) 

FinalLift = FinalLift.astype(float)

FinalLift.to_csv("LiftMatrix.csv")

# Find only top 5 attributes
attributes = set(attributes_df_new['Replace'])

attribute_counts = {}
for attr in attributes:
    attribute_counts[attr] = 0
    for comment in data['Comments']:
        if attr in comment:
            attribute_counts[attr] += 1

# Top 5 most mentioned attributes
top5attrs = sorted(attribute_counts.items(), key=lambda (k,v): v, reverse=True)[:8]
top5attrs = dict(top5attrs)
attribute_counts = sorted(attribute_counts.items(), key=lambda (k,v): v, reverse=True)
attribute_counts = dict(attribute_counts)


#create list of top brands and attributes
top5brand = top5brands.keys()
#attributelist = ["price", "part", "engine", "ease", "dealer"]
attributelist = attribute_counts.keys()

#create matrix to store results
AttrLiftMatrix = pd.DataFrame(0, index=attributelist, columns=top5brand)

#Create Dictionary to store counts of the top brand mentions in comments
#BrandProbDict = {}
#for brand in top5brand:
#	BrandProbDict[brand] = 0

#Do all the same things for attributes.  See above for details
AttrProbDict = {}
for attr in attributelist:
	AttrProbDict[attr] = 0

for x in range(len(attributelist)):
	for y in data["Comments"]:
		if attributelist[x] in y:
			AttrProbDict[attributelist[x]] +=1

probs2 = pd.DataFrame([AttrProbDict])
probs2 = probs2.transpose()
probs2 = probs2.apply(lambda x: x/len(data))

'''
#Count co-mentions in the same posts (within 300 characters), export to AttrLiftMatrix
for x in top5brand:
	for y in attributelist:
		for z in data["Comments"]:
			if x in z and y in z:
				if abs(z.index(x) - z.index(y)) <300:
					AttrLiftMatrix[x][y] += 1
			if x == y:
				AttrLiftMatrix[x][y] = 0

#create matrix to input lifts
FeatureFinalLift = pd.DataFrame(0.0, index=attributelist, columns=top5brand)

#convert # of mentions to probabilities
AttrLiftMatrix = AttrLiftMatrix.apply(lambda x: x/len(data))

#Calculate lift from probabilities
for x in top5brand:
	for y in attributelist:
		FeatureFinalLift[x][y] = float(AttrLiftMatrix[x][y]) / float((probs[0][x]) * (probs2[0][y])) 

#Write to CSV
FeatureFinalLift.to_csv("LiftFeatureMatrix.csv")

#Filter out final matrix for highest lifts.  Change .85 to increase/decrease number of pairs
for x in top5brand:
	for y in attributelist:
		if FeatureFinalLift[x][y] < .88:
			FeatureFinalLift[x][y] = 0


SentiMatrix= pd.DataFrame(0.0, index=attributelist, columns=top5brand)
CountMatrix= pd.DataFrame(0.0, index=attributelist, columns=top5brand)
for x in top5brand:
	print "Processing Brand: " + x
	for y in attributelist:
		print "Processing Attribute: " + y
		for z in data["Comments"]:
			#blob = TextBlob(z)
			#ngramlist = blob.ngrams(n=40)
			#print ngramlist[0]
			#for i in ngramlist:
			if x in z and y in z:
				if abs(z.index(x) - z.index(y)) <300:
					SentiMatrix[x][y] += pattern.en.sentiment(z[(min(z.index(x),z.index(y))-50):(max(z.index(x),z.index(y))+50)])[0]
					CountMatrix[x][y] +=1
				if z == data["Comments"][1]:
					print "Comment: " +z
					print ""
					print "Shortened Comment: " + z[(min(z.index(x),z.index(y))-50):(max(z.index(x),z.index(y))+50)]


SentiMatrix = SentiMatrix / CountMatrix			

SentiMatrix.to_csv("SentiMatrix.csv")
'''
#Calculate Lifts with Aspirational 
#create list of top brands and attributes
aspirationlist = ["aspirational"]
#create matrix to store results
AspLiftMatrix = pd.DataFrame(0, index=aspirationlist, columns=top5brand)


#Do all the same things for attributes.  See above for details
ProbDict3 = {
"aspirational" : 0
}
for x in range(len(aspirationlist)):
	for y in data["Comments"]:
		if aspirationlist[x] in y:
			ProbDict3[aspirationlist[x]] +=1

probs3 = pd.DataFrame([ProbDict3])
probs3 = probs3.transpose()
probs3 = probs3.apply(lambda x: x/len(data))

#Count co-mentions in the same posts (within 300 characters), export to liftmatrix
for x in top5brand:
	for y in aspirationlist:
		for z in data["Comments"]:
			if x in z and y in z:
				if abs(z.index(x) - z.index(y)) <300:
					AspLiftMatrix[x][y] += 1
			

#create matrix to input lifts
THEFINALMATRIX = pd.DataFrame(0.0, index=aspirationlist, columns=top5brand)
#convert # of mentions to probabilities
AspLiftMatrix = AspLiftMatrix.apply(lambda x: x/len(data))

#Calculate lift from probabilities
for x in top5brand:
	for y in aspirationlist:
		THEFINALMATRIX[x][y] = float(AspLiftMatrix[x][y]) / float((probs[0][x]) * (probs3[0][y])) 

#Write to CSV
THEFINALMATRIX.to_csv("LiftAspirationMatrix.csv")

#Filter out final matrix for highest lifts.  Change .85 to increase/decrease number of pairs
#for x in brandlist:
#	for y in attributelist:
#		if THEFINALMATRIX[x][y] < .85:
#			THEFINALMATRIX[x][y] = 0
