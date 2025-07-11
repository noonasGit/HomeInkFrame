from dataclasses import dataclass
import requests
from requests.exceptions import RequestException
import json
import time
from typing import List
import configparser
from datetime import datetime, timedelta
import os



@dataclass
class aqi_current:
    aqi_value: int
    aqi_status : str
    aqi_message : str

@dataclass
class aqi_eval:
    aqi_e_status : str
    aqi_e_message : str

@dataclass
class aqi_status_data:
    aqi_status_unknown : str
    aqi_message_unknown : str
    aqi_status_great : str
    aqi_message_great : str
    aqi_status_normal : str
    aqi_message_normal : str
    aqi_status_fair : str
    aqi_message_fair : str
    aqi_status_moderate : str
    aqi_message_moderate : str
    aqi_status_caution : str
    aqi_message_caution : str
    aqi_status_warning : str
    aqi_message_warning : str
    aqi_status_critical : str
    aqi_message_critical : str


def get_aqi_config_data(file_path:str):
    parser = configparser.ConfigParser()
    parser.read(file_path)
    data = dict()
    data['api-key-id'] = parser.get("aqi-config", "api-key")
    data['city-id'] = parser.get("aqi-config", "city")

    aqi_status_data.aqi_status_unknown = parser.get("aqi-config", "aqi_status_unknown")
    aqi_status_data.aqi_message_unknown = parser.get("aqi-config", "aqi_message_unknown")
    aqi_status_data.aqi_status_great = parser.get("aqi-config", "aqi_status_great")
    aqi_status_data.aqi_message_great = parser.get("aqi-config", "aqi_message_great")
    aqi_status_data.aqi_status_normal = parser.get("aqi-config", "aqi_status_normal")
    aqi_status_data.aqi_message_normal = parser.get("aqi-config", "aqi_message_normal")
    aqi_status_data.aqi_status_fair = parser.get("aqi-config", "aqi_status_fair")
    aqi_status_data.aqi_message_fair = parser.get("aqi-config", "aqi_message_fair")
    aqi_status_data.aqi_status_moderate = parser.get("aqi-config", "aqi_status_moderate")
    aqi_status_data.aqi_message_moderate = parser.get("aqi-config", "aqi_message_moderate")
    aqi_status_data.aqi_status_caution = parser.get("aqi-config", "aqi_status_caution")
    aqi_status_data.aqi_message_caution = parser.get("aqi-config", "aqi_message_caution")
    aqi_status_data.aqi_status_warning = parser.get("aqi-config", "aqi_status_warning")
    aqi_status_data.aqi_message_warning = parser.get("aqi-config", "aqi_message_warning")
    aqi_status_data.aqi_status_critical = parser.get("aqi-config", "aqi_status_critical")
    aqi_status_data.aqi_message_critical = parser.get("aqi-config", "aqi_message_critical")


    parser.clear
    return data

def set_aqi_status_data(aq_value:int):
    return_dict = []
    return_status = "unknown"
    return_message = "unknown"
    if aq_value == -1:
        return_status = aqi_status_data.aqi_status_unknown
        return_message = aqi_status_data.aqi_message_unknown

    if aq_value >= 0:
        return_status = aqi_status_data.aqi_status_great
        return_message = aqi_status_data.aqi_message_great
    if aq_value > 10 and aq_value <=50:
        return_status = aqi_status_data.aqi_status_normal
        return_message = aqi_status_data.aqi_message_normal
    if aq_value > 50 and aq_value <=80:
        return_status = aqi_status_data.aqi_status_fair
        return_message = aqi_status_data.aqi_message_fair
    if aq_value > 80 and aq_value <=100:
        return_status = aqi_status_data.aqi_status_moderate
        return_message = aqi_status_data.aqi_message_moderate
    if aq_value > 100 and aq_value <=150:
        return_status = aqi_status_data.aqi_status_caution
        return_message = aqi_status_data.aqi_message_caution
    if aq_value > 150 and aq_value <=200:
        return_status = aqi_status_data.aqi_status_warning
        return_message = aqi_status_data.aqi_message_warning
    if aq_value > 200:
        return_status = aqi_status_data.aqi_status_critical
        return_message = aqi_status_data.aqi_message_critical

    return_dict = aqi_eval(aqi_e_status = return_status,
                                aqi_e_message = return_message)
    return return_dict




def get_aqi_status_data(file_path:str):
    parser = configparser.ConfigParser()
    parser.read(file_path)
    data = dict()
    aqi_status_data.aqi_status_unknown = parser.get("aqi-config", "aqi_status_unknown")
    aqi_status_data.aqi_message_unknown = parser.get("aqi-config", "aqi_message_unknown")
    aqi_status_data.aqi_status_great = parser.get("aqi-config", "aqi_status_great")
    aqi_status_data.aqi_message_great = parser.get("aqi-config", "aqi_message_great")
    aqi_status_data.aqi_status_normal = parser.get("aqi-config", "aqi_status_normal")
    aqi_status_data.aqi_message_normal = parser.get("aqi-config", "aqi_message_normal")
    aqi_status_data.aqi_status_fair = parser.get("aqi-config", "aqi_status_fair")
    aqi_status_data.aqi_message_fair = parser.get("aqi-config", "aqi_status_fair")
    aqi_status_data.aqi_status_moderate = parser.get("aqi-config", "aqi_status_moderate")
    aqi_status_data.aqi_message_moderate = parser.get("aqi-config", "aqi_message_moderate")
    aqi_status_data.aqi_status_caution = parser.get("aqi-config", "aqi_status_caution")
    aqi_status_data.aqi_message_caution = parser.get("aqi-config", "aqi_message_caution")
    aqi_status_data.aqi_status_warning = parser.get("aqi-config", "aqi_status_warning")
    aqi_status_data.aqi_message_warning = parser.get("aqi-config", "aqi_message_warning")
    aqi_status_data.aqi_status_critical = parser.get("aqi-config", "aqi_status_critical")
    aqi_status_data.aqi_message_critical = parser.get("aqi-config", "aqi_message_critical")
    
    return_data = []
    return_data = aqi_status_data(aqi_status_unknown = aqi_status_data.aqi_status_unknown,
                                aqi_message_unknown = aqi_status_data.aqi_message_unknown,
                                
                                aqi_status_great = aqi_status_data.aqi_status_great,
                                aqi_message_great = aqi_status_data.aqi_message_great,

                                aqi_status_normal = aqi_status_data.aqi_status_normal,
                                aqi_message_normal = aqi_status_data.aqi_message_normal,
                                                                    
                                aqi_status_fair = aqi_status_data.aqi_status_fair,
                                aqi_message_fair = aqi_status_data.aqi_message_fair,

                                aqi_status_moderate = aqi_status_data.aqi_status_moderate,
                                aqi_message_moderate = aqi_status_data.aqi_message_moderate,

                                aqi_status_caution = aqi_status_data.aqi_status_caution,
                                aqi_message_caution = aqi_status_data.aqi_message_caution,

                                aqi_status_warning = aqi_status_data.aqi_status_warning,
                                aqi_message_warning = aqi_status_data.aqi_message_warning,

                                aqi_status_critical = aqi_status_data.aqi_status_critical,
                                aqi_message_critical = aqi_status_data.aqi_message_critical)
    parser.clear
    return return_data

def current_aqi():
    connection_error = 0
    aqi_config = dict()
    aqi_config = get_aqi_config_data("aqidata.ini")


    base_url = "https://api.waqi.info/feed/"+aqi_config['city-id']+"/"
    apikey = "token="+aqi_config['api-key-id']
    
    #Construct the entire request URL
    url = base_url+"?"+apikey
    #print("URL Constructed...")
    #print(url)
    api_error = ""
    aqierror = 0
    #print("Connecting to AQI API, current levels for "+aqi_config['city-id']+"...")
    
    for attempt in range(2):
        try:
            rawresponse = requests.get(url)
            break  # If the requests succeeds break out of the loop
        except RequestException as e:
            api_error = format(e)
            print("AQI API call failed, attempt "+str(attempt))
            time.sleep(2 ** attempt)
            aqierror = -3
            continue  # if not try again. Basically useless since it is the last command but we keep it for clarity
    try:
        url_resp=rawresponse.ok
        url_reason=rawresponse.reason
    except:
        url_resp=False
        url_reason="Unknown"

    return_data = []

    if aqierror == 0 and url_resp==True:
        try:
            json_data = rawresponse.json()
            aqi_current.aqi_value= json_data['data']['aqi']
        except:
            return_data = aqi_current(aqi_value= -1,
                                aqi_status = "unknown",
                                aqi_message = "No Data, please check back later")

        ret_aq_data = set_aqi_status_data(aqi_current.aqi_value)

        return_data = aqi_current(aqi_value= aqi_current.aqi_value,
                                aqi_status = ret_aq_data.aqi_e_status,
                                aqi_message = ret_aq_data.aqi_e_message)
                                  
    else:
        print("Error getting data from AQI API, ")
        if url_reason == "Unauthorized" :
            print("API KEY ISSUE!!")
            print("Please ensure you have entered a correct API key for transit in the openweather.ini file")
            print("####################################################################################")
            print(api_error)
        return_data = aqi_current(aqi_value= -1,
                          aqi_status = "unknown",
                          aqi_message = "No Data, please check back later")

            
    return return_data



def write_aqi_stats(file_path:str, aqi_value: int):
    ret_message = ""
    subdir = os.path.dirname(file_path)
    #print(subdir)
    if os.path.exists(subdir) == False:
        os.mkdir(subdir)
    aqi_array = []
    if os.path.exists(file_path) :
        ref_file = open(file_path, 'r')
        for rline in ref_file:
             aqi_array.append(rline)
        #print(str(len(aqi_array))+" measures loaded...")
        ref_file.close
    q_value = datetime.now().strftime("%H@")
    #print(q_value)
    #print(aqi_array)
    my_file = open(file_path, 'a')
    if len(aqi_array) > 0:
        if q_value in str(aqi_array):
            ret_message = "AQI Hour Already in stats"

        else:
            ret_message = "Adding AQI to stats hour"
            my_file.write(q_value+str(aqi_value)+'\n')
    else:
        print("File is empty...")
        print("Adding AQI to stats hour")
        my_file.write(q_value+str(aqi_value)+'\n')

    my_file.close


    

def aqi_trend(file_path:str, comp_file_path:str, aqi_value: int):
    aqi_array = []
    comp_aqi_array = []
    # Load the compare file (yesterdays file)
    if os.path.exists(comp_file_path) :
        comp_ref_file = open(comp_file_path, 'r')
        for rline in comp_ref_file:
             comp_aqi_array.append(rline)
        comp_ref_file.close
    else :
        print("Compare file : "+comp_file_path+" does not exist")
        return 404
      
    # Load todays file
    if os.path.exists(file_path) :
        ref_file = open(file_path, 'r')
        for rline in ref_file:
             aqi_array.append(rline)
        ref_file.close
    else :
        print("File not found: "+file_path)
        return 404
    #if len(comp_aqi_array) != len(aqi_array) or len(comp_aqi_array) == 0:
    #    return 500
    q = 0
    foundaqi=False
    return_value = 400
    for i in aqi_array:
        #print("its now "+str(datetime.now().hour))
        #print("Checking for value at: "+i.split("@")[0])
        if int(i.split("@")[0]) == int(datetime.now().hour) :
            #print("found it")
            foundaqi=int(i.split("@")[0])

    if foundaqi  :
        while q < len(comp_aqi_array):
            #print("At Q "+str(q)+" of "+str(len(aqi_array)))
            if int(comp_aqi_array[q].split("@")[0]) == foundaqi :
                #print("Found it")
                if int(comp_aqi_array[q].split("@")[1]) == int(comp_aqi_array[q].split("@")[1]):
                    return_value = 0
                if int(comp_aqi_array[q].split("@")[1]) > int(comp_aqi_array[q].split("@")[1]):
                    return_value = 1
                if int(comp_aqi_array[q].split("@")[1]) < int(comp_aqi_array[q].split("@")[1]):
                    return_value = -1
            q+=1
    return return_value