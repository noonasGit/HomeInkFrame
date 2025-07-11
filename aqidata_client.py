from aqidata import current_aqi, get_aqi_status_data, write_aqi_stats, aqi_trend
from datetime import date, datetime, timedelta
import os

today_aqi = current_aqi()

print("Todays AQI is: "+str(today_aqi))

aqi_status = get_aqi_status_data("aqidata.ini")

print(aqi_status.aqi_message_caution)
yesterday = datetime.now()+ timedelta(days=-1)
c_aqi_stats_file = "aqi_stats/aqi_"+yesterday.strftime("%d_%m")

aqi_stats_file = "aqi_stats/aqi_"+datetime.now().strftime("%d_%m")
#print(aqi_stats_file)


write_aqi_stats(aqi_stats_file, today_aqi)
print("Checking trend...")
trend = aqi_trend(aqi_stats_file, c_aqi_stats_file, today_aqi)
print(trend)
if trend == 1 :
    print("\u2B06") # UP
if trend == -1 :
    print("\u2B07") # DOWN

if trend == 0 :
    print("\u2B0C") # SAME
