# By Jonas Johansson
# For the KoboHUB Dashboard

from requests import get
from requests.exceptions import RequestException
from dataclasses import dataclass
import os
import random


@dataclass
class quote_summary:
    quote_text: str
    quote_author :str

def quoteoftheday():
    quote_data = ""
    qerror = 0
    try:
        response = get('http://api.quotable.io/random')
        if response.ok:
            quote_body = response.json()
            quote_text = quote_body['content'].replace('\n', '') + " "    
            quote_author = quote_body['author'].replace('\n', '') + " "
            quote_data = quote_summary(quote_text, quote_author)
            #print(response.status_code)
        else:
            quote_text = "Error getting quote, API Call failed"
            quote_author = "Quote engine"
            quote_data = quote_summary(quote_text, quote_author)

    except RequestException as e:
        print("Error getting quote, API Call failed.")
        print("Error Code: "+str(e))
        quote_text = ""
        quote_author = ""
        quote_data = quote_summary(quote_text, quote_author)

    # DEBUG AREA
    #quote_text = ""
    #quote_author = ""
    #quote_data = quote_summary(quote_text, quote_author)
    # DEBUG AREA
    return quote_data    

def addquotetofile(ref_file_path:str, file_path:str, n_quote_text:str, n_quote_author:str):
    author_block = ["Joseph Stalin","Putin","Hitler","Karl Marx"]
    quote_array = []
    ref_array = []
    if os.path.exists(ref_file_path) :
        ref_file = open(ref_file_path, 'r')
        for rline in ref_file:
             ref_array.append(rline)
        #print(str(len(ref_array))+" reference quotes loaded...")
        ref_file.close
    
    if os.path.exists(file_path) :
        my_file = open(file_path, 'a')
        if any(n_quote_text in word for word in  ref_array):
            if not n_quote_author in author_block :
                #print("Quote alredy in file")
                my_file.close
            else:
                print("Author "+n_quote_author+" blocked")
                my_file.close
        else:
            print("New quote added to file : "+file_path)
            my_file.write("\n"+n_quote_text)
            my_file.write("@"+n_quote_author)
            my_file.close
    else:
        print("Error")
        my_file.close


def quotefromfile(file_path:str):
    if os.path.exists(file_path) :
        quote_array = []
        with open(file_path) as my_file:
            for line in my_file:
                quote_array.append(line)
        #print(str(len(quote_array))+" quotes loaded...")
        ql = len(quote_array)-1
        qr_n = random.randint(0,(ql-1))
        quote_text = quote_array[qr_n].split("@")[0].replace('\n', '')
        quote_author = quote_array[qr_n].split("@")[1].replace('\n', '')
    else :
        quote_text = "No quote found"
        quote_author = "CNtablet"
    quote_data = quote_summary(quote_text, quote_author)
    return quote_data