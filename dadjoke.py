import requests
import configparser
import json
import os
import random

def getdadjoke():
    apikey = get_config_data("dadjoke.ini")
    
    limit = 1
    api_url = 'https://api.api-ninjas.com/v1/dadjokes?limit={}'.format(limit)
    
    api_headers = {}
    api_headers["X-Api-Key"] = apikey
    api_headers["accept"] = "application/json"
    #print(api_headers)
    response = requests.get(api_url, headers=api_headers)
    if response.status_code == requests.codes.ok:
        Jdadjoke = response.json()
        #print(dadjoke)
        for J in Jdadjoke:
            #print(J['joke'])
            dadjoke=J['joke']
            addtofile("dadjokes.txt","dadjokes.txt", dadjoke)
    else:
        print("Error:", response.status_code, response.text)
        dadjoke = "404 no dad or joke found ;("   
    return dadjoke

def dadjokefromfile(file_path:str):
    if os.path.exists(file_path) :
        quote_array = []
        with open(file_path) as my_file:
            for line in my_file:
                quote_array.append(line)
        #print(str(len(quote_array))+" quotes loaded...")
        ql = len(quote_array)
        qr_n = random.randint(0,(ql-1))
        joke_text = quote_array[qr_n]
    else :
        joke_text = "404 Dad Joke not found"
    return joke_text


def get_config_data(file_path:str):
    parser = configparser.ConfigParser()
    parser.read(file_path)
    data = dict()
    data['api-key-id'] = parser.get("config", "api-key")
    
    parser.clear
    return data["api-key-id"]

def addtofile(ref_file_path:str, file_path:str, n_joke_text:str, ):
    quote_array = []
    ref_array = []
    if os.path.exists(ref_file_path) :
        ref_file = open(ref_file_path, 'r')
        for rline in ref_file:
             ref_array.append(rline)
        ref_file.close
    
    if os.path.exists(file_path) :
        my_file = open(file_path, 'a')
        if any(n_joke_text in word for word in  ref_array):
            #print("Alredy in file")
             my_file.close
        else:
            #print("New joke added to file : "+file_path)
            my_file.write("\n"+n_joke_text)
            my_file.close
    else:
        print("Error")
