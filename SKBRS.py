from bs4 import BeautifulSoup 
import requests
import pymongo

def RunThis(searchString):
    """
    First Connect DB and Check it 
    """
    
    dbConn=pymongo.MongoClient("mongodb+srv://kPLjf1xsFBcEpyQu:kPLjf1xsFBcEpyQu@db.yqjqw.mongodb.net/SKBRSDB?retryWrites=true&w=majority")
    dbName='SKBRSDB'
    db=dbConn[dbName]
    collection_name=searchString.replace(" ","")
    collection=db[collection_name]
    # reviews=collection.find({})
    """
    If Found then return then and there
    """
    if collection.count_documents({})>0:
        return collection.find({}),collection.count_documents({})

    """
    Else do scrapping
    """
    url = 'https://www.flipkart.com/search?q={}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off'.format(searchString)
    
    
    data=requests.get(url)
    
    
    Text=BeautifulSoup(data.content,'html.parser')
    """
    Finding all the URLs from the FLIPKART SEARCH PAGE
    """
    
    values=Text.find_all('a',{'class':'_1fQZEK'})
    product_url=[]
    """
    There are two ways in which search pages are available.Both are covered.
    Try to search "iphone" and then "pencil". :)
    """
    if len(values)!=0:
        for half_url in values:
            product_url.append('https://www.flipkart.com'+half_url['href'])
    else:
        divInfo=Text.find_all('div',{'class':'_2pi5LC col-12-12'})
        for inidi_Div in divInfo:
            temp=inidi_Div.find_all('a',{'class':'_2rpwqI'})
            if len(temp)!=0:
                for temps in temp:
                    product_url.append('https://www.flipkart.com'+temps['href'])



    reviews=[]
    counter_reviews=0
    """
    For each Search Page find if
        there are any reviews
        If we can load more reviews
        Then Extract as we would.
    """
    for url in product_url[:20]:
        html_url=requests.get(url)
        print("Hitting: "+url+'\n')
        data_url=BeautifulSoup(html_url.content,'html.parser')
        data=data_url.find_all('div',{'class':'_2c2kV-'})
        if len(data)==1:
            """
            No Reviews Posted for that URL Product
            """
            print("No Reviews Posted for that URL Product")
            continue
        elif len(data)==2:
            """
            Reviews Less Than 4 So No 'See All Reviews'.
            """
            print("Reviews Less Than 4 So No 'See All Reviews'")
            temp=data[1].find_all('div',{'class':'_16PBlm'})
            for review in temp:
                temp_dict=dict()
                if review.findChild('p') is None:
                    continue
                try:
                    temp_dict['Name']=review.findChild('p',{'class':'_2sc7ZR _2V5EHH'}).get_text()
                except:
                    temp_dict['Name']="No Name"
                try:
                    temp_dict['Heading']=review.findChild('p').get_text()
                except:
                    temp_dict['Heading']="No Heading"

                try:
                    temp_dict['Rating']=review.findChild('p').find_previous_sibling().get_text()
                except:
                    temp_dict['Rating']="No Rating"
                try:
                    temp_dict['Body']=review.find('div',{'class':'t-ZTKy'}).findChild().findChild().get_text()
                except:
                    temp_dict['Body']="No Body"
                temp_dict['Product']=searchString
                if temp_dict not in reviews:
                    counter_reviews+=1
                    reviews.append(temp_dict)
        else:
            """
            First Get the 'See All Reviews' Link
            Second get all the Reviews from that page and subsequent pages till there are any reviews Left.
            """
            counter=0
            urls=None
            try:
                urls=prev_url='https://www.flipkart.com'+data[-1].find_next_sibling('a')['href']
            except Exception as e:
                print(e)
                print('Some Unknown Exceptions Occurred.....')
                break
            while counter<10:
                prev_url=urls
                try:
                    extractData=requests.get(urls)
                except Exception as e:
                    print(e)
                    break
                print("Hitting: "+urls+'\n')
                extractData=BeautifulSoup(extractData.content,'html.parser')
                try:
                    temp=extractData.find('div',{'class':'_1YokD2 _3Mn1Gg col-9-12'}).find_all('div',{'class':'_1AtVbE col-12-12'})
                except Exception as e:
                    print('Halted Due to Exception Occured.....')
                    print(e)
                    counter_reviews+=counter
                    break
                for review in temp:
                    temp_dict=dict()
                    if review.findChild('p') is None:
                        continue
                    try:
                        temp_dict['Name']=review.findChild('p',{'class':'_2sc7ZR _2V5EHH'}).get_text()
                    except:
                        temp_dict['Name']="No Name"
                    try:
                        temp_dict['Heading']=review.findChild('p').get_text()
                    except:
                        temp_dict['Heading']="No Heading"

                    try:
                        temp_dict['Rating']=review.findChild('p').find_previous_sibling().get_text()
                    except:
                        temp_dict['Rating']="No Rating"
                    try:
                        temp_dict['Body']=review.find('div',{'class':'t-ZTKy'}).findChild().findChild().get_text()
                    except:
                        temp_dict['Body']="No Body"
                    temp_dict['Product']=searchString
                    if temp_dict not in reviews:
                        reviews.append(temp_dict)
                        counter+=1
                        
                if extractData.find('a',{'class':'_1LKTO3'}) is None:
                    print("Halted Due to No NEXT Button")
                    counter_reviews+=counter
                    break
                someData=extractData.find_all('a',{'class':'_1LKTO3'})
                for tag in someData:
                    if tag.findChild().get_text()=='Next':
                        urls='https://www.flipkart.com'+tag['href']
                if urls==prev_url:
                    print("Halted Due to URLS Match")
                    counter_reviews+=counter
                    break
    print(len(reviews))
    if len(reviews)!=0:
        collection.insert_many(reviews,ordered=False)
    return reviews,len(reviews)