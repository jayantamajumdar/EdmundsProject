#Edmunds.com Forum scraper

# Used to pull information for sentiment analysis and 
# vehicle comparisons in the entry level luxury performance 
# sedan category


from bs4 import BeautifulSoup
import os.path
import json
import urllib2
import re
import pandas as pd


# Regular Expressions for parsing Dates and Usernames
date_regex = re.compile(r'\d{4}-\d{2}-\d{2}')
username_regex = re.compile(r'^@(\S+) .*?')


# Establish page numbers to cycle through and loop through each page
# Final output Edmunds.csv file contains all posts from the specified pages
forum_pages = range(0,500) 

# Creating soup objects for desired pages 
for page in forum_pages:
    if page%10==0:
        print "Reading page..."+str(page)
    page = urllib2.urlopen("http://forums.edmunds.com/discussion/2864/general/x/entry-level-luxury-performance-sedans/p"+str(page)).read()
    soup = BeautifulSoup(page)
    
    # Initialize dictionary to hold spaces for usernames, comments and dates in our dataframe
    # Usernames from "Username" class ; Dates using regex to extract in YYYY-MM-DD format; both used to uniquely identify comments
    # Comments extract text for analysis
    crawl_dict = {}
    crawl_dict['Usernames'] = [str(user.text) for user in soup.findAll('a', attrs={'class': 'Username'})]
    crawl_dict['Comments'] = [comment.text.encode('utf-8').strip() for comment in soup.findAll('div', attrs={'class': 'Message'})]
    crawl_dict['Dates'] = [re.findall(date_regex, date.get('datetime'))[0] for date in soup.findAll('time')]
    
    # Write to DF and append to csv file
    edmunds_df = pd.DataFrame.from_dict(crawl_dict)
    edmunds_df = pd.DataFrame(edmunds_df,columns=['Dates','Usernames','Comments'])
    if os.path.exists("Edmunds.csv"):
        edmunds_df.to_csv("Edmunds.csv", header=False)
    else:
        edmunds_df.to_csv("Edmunds.csv")

# Final Product is .csv file with all of the text, usernames and dates from the pages chosen


