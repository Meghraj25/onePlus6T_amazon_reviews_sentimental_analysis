import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017')
db = client['amazon']
collec = db.products
entry = {} 

proxies = {
    1:{'http': '157.230.13.186:8080'},
    2:{'http': '104.248.220.143:3128'},
    3:{'http': '134.209.49.222:3128'},
    4:{'http': '206.81.5.28:3128'},
    5:{'http': '206.81.4.94:8080'},
    6:{'http': '68.110.172.76:3128'},
    7:{'http': '159.65.164.58:80'},
    8:{'http': '51.38.80.159:80'},
    9:{'http': '54.37.31.169:80'},
    10:{'http': '96.65.221.1:59161'}
}

#Fetching Main product Page
sourceCode = requests.get('https://www.amazon.in/OnePlus-Midnight-Black-128GB-Storage/dp/B07DJHY82F/ref=cm_cr_arp_d_product_top?ie=UTF8',headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}, proxies=proxies)
plaintext = sourceCode.text
soup = BeautifulSoup(plaintext)

link = soup.find('span',{'id':'productTitle'})
title = link.string
strTitle = title.strip()
entry['ProductTitle'] = strTitle

#Product Description

desc = soup.find('div',{'id':'feature-bullets'}).find("ul")
descr = desc.strings
descrp = list(descr)
seperator = ','
entry['ProductDescription'] = seperator.join(descrp)

#Product Image
img = soup.find('img',{'alt': strTitle})
imgp = img['src']
entry['ProductEnlargeImage'] = imgp

#Product Price (With Exchange and Without Exchange)

wex = soup.find('div',{'id':'maxBuyBackDiscountSection'}).find("span")
wexc = wex.strings
wexch = list(wexc)
seperator = ' '
entry['PriceWithExchange'] = seperator.join(wexch)

pri = soup.find('span',{'id':'priceblock_dealprice'})
pric = pri.strings
price = list(pric)
seperator = ' '
entry['PriceWithoutExchange'] = seperator.join(price).strip()

#Product Colours

colours = []
for cl in soup.find_all('img',{'class':'imgSwatch'}):
    clrs = cl['alt']
    colours.append(clrs)
    
sep = ' , '
entry['ProductColours'] = sep.join(colours)

#Total Reviews

rewc = soup.find('h2',{'data-hook':'total-review-count'})
rewco = rewc.string
entry['TotalReviews'] = rewco

#Star Rating

arat = soup.find('span',{'data-hook':'rating-out-of-text'})
arating = arat.string
entry['StarRating'] = arating

#Technical Details

techdata = []
table = soup.find('div', attrs={'class':'pdTab'}).find('table')

for rows in soup.find('div', attrs={'class':'pdTab'}).find('table').find_all('tr'):
    
    rowst = rows.strings
    rowstl = list(rowst)
    sep1 = ':'
    techdata.append(sep1.join(rowstl).strip())

entry['TechnicalDetails'] = sep.join(techdata).strip()


#View All Reviews Page URL
moreR = soup.find('a',{'data-hook':'see-all-reviews-link-foot'})
moreRe = moreR['href']


#Fetching recent 100 Reviews

allreviews={}
k = 1
for i in range(1,11):
    moreReviewsURL = 'https://www.amazon.in'+moreRe+'&sortBy=recent&pageNumber='+str(i)
    sourceCode = requests.get(moreReviewsURL,headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}, proxies=proxies[i])
    plaintext = sourceCode.text
    soup = BeautifulSoup(plaintext)
    
    for review in soup.find_all('span',{'data-hook':'review-body'}):
        reviews = review.find('span').string
        allreviews[str(k)] = reviews
        k += 1

entry['MostRecent100Reviews'] = allreviews

result = collec.insert_one(entry)
print(result)

