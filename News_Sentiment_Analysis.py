# -*- coding: utf-8 -*-

#############################################################################################
###############################Step 01: Scrapes urls from the google search results##########
#############################################################################################

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#import selenium 
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import random,os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
def writeToFile(links,webp,company,date,month,year):
	try:
		os.makedirs('links')
	except Exception as e:
		pass
	try:
		os.makedirs(os.path.join(BASE_PATH,'links',str(company),str(webp),str(year)[-2:]))
	except Exception as e:
		pass
	
	f = open(os.path.join(BASE_PATH,"links",company,webp,str(year)[-2:],"results_"+webp+"_"+company+"_"+date+"_"+month+"_"+year+'.data'),'a+')
	for i,j in links:
		f.write(str(i)+"::"+str(j)+"\n")
	f.close()
driver_path = ''

if os.name == 'nt':
	driver_path = os.path.join(os.path.dirname(BASE_PATH),"Scripts")+'\chromedriver.exe'
elif os.name == 'posix':
	driver_path = os.environ['HOME']+'/beautiful_soup/chromedriver'
else:
	driver_path = None

print("#"*8+" Enter the details to scrape separated by SPACE.")
sd,sm,sy=input("Enter starting day month year ").split(" ")
ed,em,ey=input("Enter ending day month year ").split(" ")
webp=input("Enter website to scrape- ")
comp=input("Enter company data to scrape -")


driver = webdriver.Chrome(executable_path=driver_path)
driver.implicitly_wait(15)
start_url="https://www.google.co.in/search?num=100&biw=1040&bih=635&tbs=cdr%3A1%2Ccd_min%3A"+"{smonth}"+r"%2F"+"{sday}"+r"%2F"+"{syear}"+r"%2Ccd_max%3A"+"{emonth}"+r"%2F"+"{eday}"+r"%2F"+"{eyear}"+r"%2Csbd%3A1&tbm=nws&q=site%3A"+"{webpage}+%22{company}%22&&oq=site%3A{webpage}"+"%22{company}%22&gs_l=serp.3...0.0.0.1565.0.0.0.0.0.0.0.0..0.0....0...1c..64.serp..0.0.0.IfKqhHBbtbY"
driver.get(start_url.format(smonth=sm,sday=sd,syear=sy,emonth=em,eday=ed,eyear=ey,webpage=webp,company=comp))
data={}
date=[]
next_page=""
wait = WebDriverWait(driver, random.randint(10,15))
i=0
time.sleep(random.randint(5,10))
previous=next_page
try:
	while next_page is not None or previous is not None:
		print(i)
		if i >= 1:#no of pages to browse
			break
		#time.sleep(random.randrange(5,10))  #no need for pages = 1
		list_links=[]
		dat = []
		list_links=[]
		try:
			next_page = wait.until(EC.element_to_be_clickable((By.ID,'navcnt')))
			next_page = driver.find_element_by_link_text('Next')
			element=driver.find_elements_by_xpath("*//h3/a")

			dat = driver.find_elements_by_xpath('//*[@id="rso"]/div/div/div/div/div[1]/span[3]')
		except Exception as e:
			print (e)
			next_page=None
			#this is for the last page when no next option will be available
			element=driver.find_elements_by_xpath("*//h3/a")

			dat = driver.find_elements_by_xpath('//*[@id="rso"]/div/div/div/div/div[1]/span[3]')
			
		for ele in element:
			list_links.append(ele.get_attribute("href"))
		
		for d in dat:
			date.append(d.text);

		data[i]=list_links
		for ele in element:
			list_links.append(ele.get_attribute("href"))

		list_links = zip(date,list_links)

		writeToFile(list_links,webp,comp,sd,sm,sy)
		i+=1
		if next_page is not None:
			next_page.click()
		else:
			break
except Exception as e:
	print(e)

finally:
	print("*"*8+"Finished fetching all the urls"+"*"*8)
	count=0
	for i in data.keys():
		count+=len(data[i])
	print("#"*8+"Fetched "+str(count))
       
import requests
import os
from bs4 import BeautifulSoup
from scrape_with_bs4 import sc_reuters, sc_ft
from nltk.tokenize import sent_tokenize
# checks for the presence of a word in a string by checking character before 
#the start of the word and after the end of the word
def search_key(input_string,word):
		index=input_string.find(word)
		if(index!=-1):
			if(index!=0):
				low=ord(input_string[index-1])
			else:
				low=95
			if(index+len(word)!=len(input_string)):
				high=ord(input_string[index+len(word)])
			else:
				high=95
			if( (low<97 or low>122) and ( high<97 or high>122) ):
				return True
			else:
				return search_key(input_string[index+len(word):],word)
		else:
			return False
NEWS={
	'reuters.com':sc_reuters,
	'financialtimes.com': sc_ft
	}
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(BASE_PATH,'links'))
print("Enter company name to filter results for among ")
print([ i for i in os.listdir() if 'empty.txt' not in i])
company=input()
print("Chose option regarding file name:\n ",
		"1. Keep old file and new name is old name appended with _\n",
		" 2. Overwrite old file\n")
name_change=input()
if name_change=='1':
	name_change='_'
else:name_change=''
print(name_change)
for path, subdirs, files in os.walk(os.path.join(BASE_PATH,'links',company)):
		#avoids archive subdir and its path
		if(path.rfind('archive')==-1 and len(files)!=0):
			print(files)
			for file in files:
				filtered_links=[]
				print("Filtering for "+file)
				with open(path+'/'+file, 'r') as in_file:
					links = [line.rstrip('\n') for line in in_file]
				for key in NEWS:
					if key in file:
						for url in links:
							try:
								print(url)
								#checks for the inurl presence of the company name
								if(search_key(url.lower(),company.lower())):
									filtered_links.append(url)
									print("*"*8+"Passed")
									continue
								count=0
								r = requests.get(url.split('::')[1])
								soup = BeautifulSoup(r.content,"html.parser")			
								#extracts content from the respective scraper
								list_of_sentences=NEWS[key](soup)	
								tokens=[]
								for x in list_of_sentences:
									tokens.extend(sent_tokenize(str(x)))
								for tk in tokens:
									if(search_key(tk.lower(),company)):
										count+=1
								if(count>=2):
									filtered_links.append(url)
									print("count-"+str(count))
							except Exception as e:
								print(e)
				wfile=open(path+'/'+file+name_change,'w+')
				for lnk in filtered_links:
					wfile.write(lnk)
					wfile.write('\n')
				wfile.seek(0,0)
				print('#'*12)
				print("##written "+str(len(filtered_links)))
				wfile.close()
				print("##original "+str(len(links)))
				print('#'*12)

#############################################################################################
#####Step 02: Merge the data collected from google search results and news archive###########
#############################################################################################

import os
import glob
from difflib import SequenceMatcher
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def inp():
	print("1)Merge File\n2)Get full data\n")
	i = input()
	if i == '1':
		inp = input('Enter the company to merge\n')
		return inp
	else:
		company = input('Enter company for full data processing\n')
		file = 'results_'+company+'_full.data'
		links = [line.rstrip('\n') for line in open(os.path.join(BASE_PATH,'links',company,file))]
		links = list(set(links)) #assuming date will be same for archive as well as google results
		print(len(links))
		writeToFile(links,company)

		f = open(os.path.join(BASE_PATH,'links','finallinks',"results_"+company+'_unique.data'),'a+')
		for i in links:
			f.write(str(i)+"\n")
		f.close()


		print("All Done!")
		return None

def listArchiveFiles(company):
	for path, subdirs, files in os.walk(os.path.join(BASE_PATH,'links',company,'archive')):
		if len(files) > 0:
			return files[0]

def countFiles(company):
	a = []
	b = []
	writeToFile([0],company,'random')#creating random file..function stops working without a file in folder
	filew = os.path.join(BASE_PATH,'links',company,"results_random_unique.data")
	for path, subdirs, files in os.walk(os.path.join(BASE_PATH,'links',company)):
			if len(files) > 0:
				for i in subdirs:
					cnt = sum([len(files) for r, d, files in os.walk(os.path.join(BASE_PATH,'links',company,i))])
					a.append(cnt)
	os.remove(filew)#removing random file
	return a				

def listGoogleFiles(company):
	if company != None:
		a = []
		b = []
		k = 0
		p = 2
		s = {}
		index = 1
		count = countFiles(company)
		max_size = len(count)

		for path, subdirs, files in os.walk(os.path.join(BASE_PATH,'links',company)):
			if len(files) > 0:
				
				for i in files:
					if 'archive' in i.lower():
						b.append(os.path.join(path,i))
					else:
						a.append(os.path.join(path,i))

						if index < max_size :
							if len(a) == count[index]:
								temp = []
								s.update({p:temp+a})
								a.clear()
								p+=1
								index+=1
						
		files = []
		s[1] = b
		websites = {1:'archive',2:'economictimes.indiatimes.com',3:'moneycontrol.com',4:'ndtv.com',5:'reuters.com',6:'thehindu.com',7:'thehindubusinessline.com'}
	
		for key in s:
			if key == 1:#for archive
				getUniqueLinks(s[key],websites[key],company)
			else:
				getUniqueLinks(s[key],websites[key],company)

		files.clear()
		for file in os.listdir(os.path.join(BASE_PATH,'links',company)):
			if file.endswith('.data'):
				files.append(file)
		
		getLinks(files,company)
		

def writeToFile(links,company,name=None):
	if name == None:
		f = open(os.path.join(BASE_PATH,'links',company,"results_"+company+'_unique.data'),'a+')
	else:
		f = open(os.path.join(BASE_PATH,'links',company,"results_"+name+'_unique.data'),'a+')
	for i in links:
		f.write(str(i)+"\n")
	f.close()

def getLinks(files,company):
	#print(files)
	file = os.path.join(BASE_PATH,'links',company,'results_'+company+'_full.data')
	with open(file, 'wb') as outfile:
		for f in files:
			with open(os.path.join(BASE_PATH,'links',company,f), "rb") as infile:
				outfile.write(infile.read())
	return file

def getUniqueLinks(files,website,company):
	filew = os.path.join(BASE_PATH,'links',company,'results_'+website+'_unique.data')
	print("Working for: ",website)
	with open(filew, 'w+') as outfile:
		for f in files:
			links = [line.rstrip('\n') for line in open(f)]
			if website == 'archive':
				links = checkUnique(company,links)
				print(f)
				writeToFile(links,company,str(f).split('/')[-1].split('_')[1])
			for i in links:
				outfile.write(str(i)+"\n")


	outfile.close()

def checkUnique(company,links):
	# if company != None:
	# 	file = listGoogleFiles(company)
		
	# 	links = [line.rstrip('\n') for line in open(file)]
	stats={0.2:0,0.4:0,0.6:0,0.8:0,1:0}
	count=0
	a = len(links)
	print(a)
	d = a*a
	

	c = 0
	for i in links:		
		for j in links:
			if(i!=j):
				value = SequenceMatcher(None, i, j).ratio()
				if(value<=0.2):
					stats[0.2]+=1
				elif(value<=0.4):
					stats[0.4]+=1
				elif(value<=0.6):
					stats[0.6]+=1
				elif(value<=0.7):
					stats[0.8]+=1
				elif(value>0.8):
					stats[1]+=1
					links.remove(j)
			c+=1
			b = len(links)*len(links)
		print("%\r",int((1-(b-c)/d)*100),end='')

	print("Stats for this file\n\nSimilarity Score(<=) \t occurances")
	for i in stats:
		print ('\t'+str(i)+'\t\t\t'+str(stats[i]))
	print("final count ",len(links))
	
	return links
	# if company != None:
	# 	writeToFile(links,company)
	# else:
	# 	return links



listGoogleFiles(inp())

#############################################################################################
#####Step 03: Calculate the sentiment of the collected data##################################
#############################################################################################

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import pandas as pd
import numpy as np
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

sid = SentimentIntensityAnalyzer()

def analyze(file):
    df = pd.read_csv(file)
    sent = {}
    pos = []
    neg = []
    com = []
    neu = []
    print(len(df))
    i = 0
    for date, data in df.iterrows():
        i+=1
        sent[i] = sid.polarity_scores(str(data['data']))
        pos.append(sent[i]['pos'])
        neg.append(sent[i]['neg'])
        neu.append(sent[i]['neu'])
        com.append(sent[i]['compound'])

    df['positive'] = pos
    df['negative'] = neg
    df['neutral'] = neu
    df['compound'] = com

    df.to_csv(file.split('.csv')[0]+'_sentiment'+'.csv')
    #print(df.head())

if __name__ == '__main__':
    i = input("Enter the company\n[hdfc,maruti-suzuki,itc,tcs,sbi,ongc,sun-pharma\n")

    for path, subdirs, files in os.walk(os.path.join(BASE_PATH,'content',i)):
        for f in files:
            if f.endswith('.csv'):
                f = os.path.join(BASE_PATH,'content',i,f.split('_')[3],f)
                print(f)
                analyze(f)
                

