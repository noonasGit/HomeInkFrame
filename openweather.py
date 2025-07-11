from dataclasses import dataclass
import requests
from requests.exceptions import RequestException
import json
import time
from typing import List
import configparser
from datetime import datetime, timedelta



@dataclass
class weather_forecast:
    date: int
    temperature: float
    temp_low: float
    temp_high: float
    feels_like : float
    condition: str
    pop : int
    total_pop :int
    rain : dict
    snow : dict
    # icon's path
    icon: str

@dataclass
class weather_current:
    city: str
    temperature: float
    temp_high: float
    temp_low: float
    feelslike: float
    pressure: float
    humidity: float
    wind: float
    wind_conditions : str
    condition: str
    desciption: str
    icon: str
    sun_rise: int
    sun_set : int
    error : int

@dataclass
class air_current:
    aqi: int
    co: float
    no: float
    no2: float
    o3: float
    so2: float
    pm2_5: float
    pm10: float
    nh3: float


def get_weather_config_data(file_path:str):
    parser = configparser.ConfigParser()
    parser.read(file_path)
    data = dict()
    data['api-key-id'] = parser.get("weather-config", "api-key")
    data['lat-id'] = parser.get("weather-config", "lat")
    data['lon-id'] = parser.get("weather-config", "lon")
    data['units-id'] = parser.get("weather-config", "units")
    data['lang-id'] = parser.get("weather-config", "lang")
    parser.clear
    return data

def current_weather():
    connection_error = 0
    weather_config = dict()
    weather_config = get_weather_config_data("openweather.ini")


    base_url = "http://api.openweathermap.org/data/2.5/weather"
    apikey = "APPID="+weather_config['api-key-id']
    lat = "lat="+weather_config['lat-id']
    lon = "lon="+weather_config['lon-id']
    lang = "lang="+weather_config['lang-id']
    units = "units="+weather_config['units-id']
    


    #Construct the entire request URL
    url = base_url+"?"+apikey+"&"+lat+"&"+lon+"&"+units+"&"+lang
    #print("URL Constructed...")
    #print(url)
    api_error = ""
    werror = 0
    #print("Connecting to Weather API, current weather...")
    
    for attempt in range(2):
        try:
            rawresponse = requests.get(url)
            break  # If the requests succeeds break out of the loop
        except RequestException as e:
            api_error = format(e)
            print("OpenWeather API call failed, attempt "+str(attempt))
            time.sleep(2 ** attempt)
            werror = -3
            continue  # if not try again. Basically useless since it is the last command but we keep it for clarity
    try:
        url_resp=rawresponse.ok
        url_reason=rawresponse.reason
    except:
        url_resp=False
        url_reason="Unknown"

    if werror == 0 and url_resp==True:
        return_data = []
        json_data = rawresponse.json()
        for i in json_data['weather']:
            weather_current.condition = i['main']
            weather_current.desciption = i['description']
            weather_current.icon = i['icon']


        
            weather_current.temperature = json_data['main']['temp']
            weather_current.feelslike = json_data['main']['feels_like']
            weather_current.temp_low = json_data['main']['temp_min']
            weather_current.temp_high = json_data['main']['temp_max']
            weather_current.pressure = json_data['main']['pressure']
            weather_current.humidity = json_data['main']['humidity']
            weather_current.wind = json_data['wind']['speed']
            w_text = ""
            windkmh = round( (weather_current.wind*3600)/1000,2)
            if windkmh <= 5 :
                w_text = "Still wind"
            if windkmh >5 and windkmh <= 10 :
                w_text = "Calm wind"
            if windkmh >10 and windkmh <= 25 :
                w_text = "Gusts"
            if windkmh >25 and windkmh <= 80 :
                w_text = "Winds"
            if windkmh >80 and windkmh <= 120 :
                w_text = "Storms"
            if windkmh >120:
                w_text = "Hurricane"
            weather_current.wind_conditions = w_text
            #weather_current.wind_gust = json_data['wind']['gust']
            weather_current.city = json_data['name']
            weather_current.sun_rise = json_data['sys']['sunrise']
            weather_current.sun_set = json_data['sys']['sunset']

            return_data = weather_current(city=weather_current.city,
                                   temperature=weather_current.temperature,
                                   temp_high=weather_current.temp_high,
                                   temp_low=weather_current.temp_low,
                                   feelslike=weather_current.feelslike,
                                   pressure=weather_current.pressure,
                                   humidity=weather_current.humidity,
                                   wind=weather_current.wind,
                                   wind_conditions=weather_current.wind_conditions,
                                   condition=weather_current.condition,
                                   desciption=weather_current.desciption,
                                   sun_rise=weather_current.sun_rise,
                                   sun_set=weather_current.sun_set,
                                   error=connection_error,
                                   icon=weather_current.icon)


        return return_data
    else:
        print("Error gettin data from OpenMapWeather API, "+url_reason)
        connection_error = 404
        return_data = weather_current(city="Error",
                          temperature=0,
                          temp_high=0,
                          temp_low=0,
                          feelslike=0,
                          pressure=0,
                          humidity=0,
                          wind=0,
                          wind_conditions="No data",
                          condition="No Data",
                          desciption="No Data",
                          sun_rise=0,
                          sun_set=0,
                          error=connection_error,
                          icon="EE")

        if werror != 0:
            if url_reason == "Unauthorized" :
                print("Error gettin data from OpenMapWeather API, "+url_reason)
                print("API KEY ISSUE!!")
                print("Please ensure you have entered a correct API key for Weather in the openweather.ini file")
                print("####################################################################################")
                print(api_error)
        return return_data


def get_forecast(numbdays:int):

    weather_config = dict()
    weather_config = get_weather_config_data("openweather.ini")


    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    apikey = "APPID="+weather_config['api-key-id']
    lat = "lat="+weather_config['lat-id']
    lon = "lon="+weather_config['lon-id']
    lang = "lang="+weather_config['lang-id']
    units = "units="+weather_config['units-id']
    days = "cnt="+str(numbdays)
    


    #Construct the entire request URL
    url = base_url+"?"+apikey+"&"+lat+"&"+lon+"&"+units+"&"+lang+"&"+days
    #print("URL Constructed...")
    #print(url)
    api_error = ""
    #print("Connecting to Weather API, forecast...")
    werror = 0
    for attempt in range(2):
        try:
            rawresponse = requests.get(url)
            break  # If the requests succeeds break out of the loop
        except RequestException as e:
            api_error = format(e)
            print("API call failed, attempt "+str(attempt))
            time.sleep(2 ** attempt)
            werror = -3
            continue  # if not try again. Basically useless since it is the last command but we keep it for clarity
    try:
        url_resp=rawresponse.ok
        url_reason=rawresponse.reason
    except:
        url_resp=False
        url_reason="Unknown"

    if werror == 0 and url_resp==True:
        return_data = []
        json_data = rawresponse.json()
        for i in json_data['list']:
            weather_forecast.date = datetime.utcfromtimestamp(i['dt'])
            
            weather_forecast.temp_high = i['main']['temp_max']
            weather_forecast.temp_low = i['main']['temp_min']
            weather_forecast.feels_like = i['main']['feels_like']
            weather_forecast.condition = i['weather'][0]['description']
            weather_forecast.pop = i['pop']
            weather_forecast.icon = i['weather'][0]['icon']
            try :
                weather_forecast.rain = i['rain']['3h']
                weather_forecast.rain_mm = int(i['rain']['3h'])
                #print(i['rain'])
                #print(weather_forecast.rain['3h'])
            except:
                weather_forecast.rain = 0
            try :
                weather_forecast.snow =i['snow']['3h']
                weather_forecast.snow_mm = int(i['snow']['3h'])
                #print(i['snow'])
            except:
                weather_forecast.snow = 0

            dayofweather = weather_forecast.date
            return_data.append(weather_forecast(temp_high=weather_forecast.temp_high,
                                temp_low=weather_forecast.temp_low,
                                feels_like=weather_forecast.feels_like,
                                condition=weather_forecast.condition,
                                pop=weather_forecast.pop,
                                rain=weather_forecast.rain,
                                snow=weather_forecast.snow,
                                icon=weather_forecast.icon,
                                date=weather_forecast.date))
        return return_data
    else:
        print("Error getting forecast: "+url_reason)
        return_data=[]
        return_data.append(weather_forecast(temp_high=0,
                            temp_low=0,
                            feels_like=0,
                            condition="Error",
                            pop=0,
                            rain={'3h': 0},
                            snow={'3h': 0},
                            icon="EE",
                            date=datetime.now()))
        if werror != 0:
            if url_reason == "Unauthorized" :
                print("Error gettin data from OpenMapWeather API, "+url_reason)
                print("API KEY ISSUE!!")
                print("Please ensure you have entered a correct API key for Weather in the openweather.ini file")
                print("####################################################################################")
                print(api_error)
        return return_data

def tomorrow_weather():
    day_offset = 0
    tomorrow_day = datetime.now() + timedelta(days=day_offset)
    tomorrow_ref = tomorrow_day.date()
    weather_forecast.total_pop = 0

    weather_config = dict()
    weather_config = get_weather_config_data("openweather.ini")


    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    apikey = "APPID="+weather_config['api-key-id']
    lat = "lat="+weather_config['lat-id']
    lon = "lon="+weather_config['lon-id']
    lang = "lang="+weather_config['lang-id']
    units = "units="+weather_config['units-id']
    
    return_data = []
    return_data: List[weather_forecast]

    #Construct the entire request URL
    url = base_url+"?"+apikey+"&"+lat+"&"+lon+"&"+units+"&"+lang
    #print("URL Constructed...")
    #print(url)
    api_error = ""
    werror = 0
    #print("Connecting to Weather API, forecast, one second...")
    
    for attempt in range(2):
        try:
            rawresponse = requests.get(url)
            break  # If the requests succeeds break out of the loop
        except RequestException as e:
            api_error = format(e)
            print("API call failed, attempt "+str(attempt))
            time.sleep(2 ** attempt)
            werror = -3
            continue  # if not try again. Basically useless since it is the last command but we keep it for clarity
    
    try:
        url_resp=rawresponse.ok
        url_reason=rawresponse.reason
        #print(url_resp)
        #print(url_reason)
    except:
        url_resp=False
        url_reason="Unknown"
        print("We have an issue with forecasts")

    if werror == 0 and url_resp==True:
        json_data = rawresponse.json()
        for i in json_data['list']:
            tomorrow_check = datetime.utcfromtimestamp(i['dt'])
            tomorrow_check = tomorrow_check.date()
            #print("tomorrow check "+str(tomorrow_check))
            #print("tomorrow ref "+str(tomorrow_ref))
            #print(i['dt'])
            #print(datetime.utcfromtimestamp(i['dt']))
            #print(i['pop'])
            if i['pop'] > weather_forecast.total_pop:
                weather_forecast.total_pop = i['pop']
                #print("now at "+str(weather_forecast.total_pop))
            if tomorrow_check >= tomorrow_ref :
                #print("Next day")
                day_offset +=1

                tomorrow_day = datetime.now() + timedelta(days=day_offset)
                tomorrow_ref = tomorrow_day.date()

                weather_forecast.date = datetime.utcfromtimestamp(i['dt'])
                weather_forecast.temperature = i['main']['temp']
                weather_forecast.temp_high = i['main']['temp_max']
                weather_forecast.temp_low = i['main']['temp_min']
                weather_forecast.feels_like = i['main']['feels_like']
                weather_forecast.condition = i['weather'][0]['description']
                weather_forecast.icon = i['weather'][0]['icon']
                weather_forecast.pop = i['pop']
                
                try :
                    weather_forecast.rain = i['rain']['3h']
                    weather_forecast.rain_mm = int(i['rain']['3h'])
                    #print(i['rain'])
                    #print("Rain"+str(weather_forecast.rain))
                except:
                    weather_forecast.rain = 0
                try :
                    weather_forecast.snow =i['snow']['3h']
                    #print(i['snow'])
                except:
                    weather_forecast.snow = 0

                return_data.append(weather_forecast(date=weather_forecast.date,
                                        temperature=weather_forecast.temperature,
                                        temp_high=weather_forecast.temp_high,
                                        temp_low=weather_forecast.temp_low,
                                        feels_like=weather_forecast.feels_like,
                                        condition=weather_forecast.condition,
                                        pop=weather_forecast.pop,
                                        total_pop = weather_forecast.total_pop,
                                        rain=weather_forecast.rain,
                                        snow=weather_forecast.snow,
                                        icon=weather_forecast.icon))
                
        return return_data
    else:
        print("Error forecast "+url_reason)
        print("Buffering with error data...")
        return_data.append(weather_forecast(date=datetime.now(),
                temperature=0,
                temp_high=0,
                temp_low=0,
                feels_like=0,
                condition="ERROR",
                pop=0,
                total_pop=0,
                rain=0,
                snow=0,
                icon="EE"))
        #Add second entry for next day.
        return_data.append(weather_forecast(date=datetime.now()+timedelta(days=1),
                temperature=0,
                temp_high=0,
                temp_low=0,
                feels_like=0,
                condition="ERROR",
                pop=0,
                total_pop=0,
                rain=0,
                snow=0,
                icon="EE"))
        if werror != 0:
            if url_reason == "Unauthorized" :
                print("Error gettin data from OpenMapWeather API, "+url_reason)
                print("API KEY ISSUE!!")
                print("Please ensure you have entered a correct API key for Weather in the openweather.ini file")
                print("####################################################################################")
                print(api_error)
        return return_data

def get_air_levels():
    connection_error = 0
    weather_config = dict()
    weather_config = get_weather_config_data("openweather.ini")


    base_url = "http://api.openweathermap.org/data/2.5/air_pollution"
    apikey = "appid="+weather_config['api-key-id']
    lat = "lat="+weather_config['lat-id']
    lon = "lon="+weather_config['lon-id']
    


    #Construct the entire request URL
    url = base_url+"?"+apikey+"&"+lat+"&"+lon
    #print("URL Constructed...")
    #print(url)
    api_error = ""
    werror = 0

    #print("Connecting to Weather API, current air pollutants...")
    #print(url)


    for attempt in range(2):
        try:
            rawresponse = requests.get(url)
            break  # If the requests succeeds break out of the loop
        except RequestException as e:
            api_error = format(e)
            print("API call failed, attempt "+str(attempt))
            time.sleep(2 ** attempt)
            werror = -3
            continue  # if not try again. Basically useless since it is the last command but we keep it for clarity
    try:
        url_resp=rawresponse.ok
        url_reason=rawresponse.reason
    except:
        url_resp=False
        url_reason="Unknown"

    #print(rawresponse.ok)   

    #print(rawresponse.text)

    if werror == 0 and url_resp == True:
        return_data = []
        json_data = rawresponse.json()
        for i in json_data['list']:
            air_current.aqi = i['main']['aqi']
            air_current.co = i['components']['co']
            air_current.no = i['components']['no']
            air_current.no2 = i['components']['no2']
            air_current.o3 = i['components']['o3']
            air_current.so2 = i['components']['so2']
            air_current.pm2_5 = i['components']['pm2_5']
            air_current.pm10 = i['components']['pm10']
            air_current.nh3 = i['components']['nh3']

            

            return_data = air_current(aqi=air_current.aqi,
                                   co=air_current.co,
                                   no=air_current.no,
                                   no2=air_current.no2,
                                   o3=air_current.o3,
                                   so2=air_current.so2,
                                   pm2_5=air_current.pm2_5,
                                   pm10=air_current.pm10,
                                   nh3=air_current.nh3)
        return return_data
    else:
        print("Error gettin data from OpenMapWeather API, "+url_reason)
        return_data = air_current(aqi=-1,
                                   co=-1,
                                   no=-1,
                                   no2=-1,
                                   o3=-1,
                                   so2=-1,
                                   pm2_5=-1,
                                   pm10=-1,
                                   nh3=-1)

        if werror != 0:
            if url_reason == "Unauthorized" :
                print("Error gettin data from OpenMapWeather API, "+rawresponse.reason)
                print("API KEY ISSUE!!")
                print("Please ensure you have entered a correct API key for Weather in the openweather.ini file")
                print("####################################################################################")
                print(api_error)
                connection_error = 404
        return return_data
