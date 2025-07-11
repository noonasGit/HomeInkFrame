from openweather import current_weather, get_forecast, tomorrow_weather, get_air_levels
from datetime import date, datetime

#today_air = get_air_levels()
#print("AQI: "+str(today_air.aqi))




today_weather = current_weather()
if today_weather.error == 404:
    print("Error Getting weather...")

tomorrow_w = tomorrow_weather()
print(str(len(tomorrow_w)))
tomorrows_weather = tomorrow_w[0]
#fcast=get_forecast(2)

print("City: "+today_weather.city)
print("Condition: "+today_weather.condition)
print("Descr.: "+today_weather.desciption)
print("Temp: "+str(today_weather.temperature))
print("High: "+str(today_weather.temp_high))
print("Low: "+str(today_weather.temp_low))
print("Feels like: "+str(today_weather.feelslike))
windkmh = (today_weather.wind*3600)/1000
print("Wind: "+str(today_weather.wind)+"m/s - or - "+str(windkmh)+" km/h")
popp = tomorrows_weather.pop * 100
if today_weather.error == 404:
    print("Error Getting rain")
else:
    print(tomorrows_weather.rain)
    print("PoP: "+str(int(popp))+"% with "+str(tomorrows_weather.rain)+"mm")
print("Humidity: "+str(today_weather.humidity))
print("Pressure: "+str(today_weather.pressure))

sunrise=datetime.fromtimestamp(today_weather.sun_rise).strftime('%H:%M')
print("Sunrise: "+sunrise)
sunset=datetime.fromtimestamp(today_weather.sun_set).strftime('%H:%M')
print("Sunset: "+sunset)

print("Error: "+str(today_weather.error))

print("Icon: "+today_weather.icon)

#tomorrow_weater = get_forecast(2)
#get_forecast(2)

print(str(len(tomorrow_w))+" Days returned")
if len(tomorrow_w) > 0 :
    next_day = tomorrow_w[0]
    print(next_day.date)
    print("High: "+str(next_day.temp_high))
    print("Low: "+str(next_day.temp_low))
    print("Feels Like: "+str(next_day.feels_like))
    print("Condition: "+next_day.condition)
    print('Pop: '+str(next_day.pop))
    if today_weather.error == 404:
        print("Error Getting rain")
    else:
        if next_day.rain > 0:
            print("Rain: "+str(next_day.rain)+" mm")
        if next_day.snow > 0:
            print("Snow: "+str(next_day.snow)+" mm")
        if len(tomorrow_w) >= 1:
            print("---")
    
    if len(tomorrow_w) == 1:
        print("Not enough weather")
    else:
        next_day = tomorrow_w[1]
        print(next_day.date)
        print("High: "+str(next_day.temp_high))
        print("Low: "+str(next_day.temp_low))
        print("Feels Like: "+str(next_day.feels_like))
        print("Condition: "+next_day.condition)
        print('Pop: '+str(next_day.pop))
        if next_day.rain > 0:
            print("Rain: "+str(next_day.rain)+" mm")
        if next_day.snow > 0:
            print("Snow: "+str(next_day.snow)+" mm")
