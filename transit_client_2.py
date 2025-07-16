from datetime import date, time, datetime, timezone
import time
from transit import gettransitdepartures
import zoneinfo



#Bus schedule
t = datetime.now()
print(t)
b = 0
b2 = 0

bus_times = []
#draw.text((x, y), "70", font=self.fonts.larger, fill=black)
#bus_w, bus_h = draw.textsize("00:00", font=self.fonts.SFCompact)
#x = (bx + int((bus_icon.size[0]/2)) ) - int( (bus_w/2) )
bus_times = gettransitdepartures(datetime.now(),"api_key_here","STM:102508")
bus_times2 = gettransitdepartures(datetime.now(),"api_key_here","STM:102503")

#bus_times = get70departures(datetime.now(),"enter-key-here")
print("Getting Transit times...")
if len(bus_times) == 0:
    print("No live bus times goten")
#print(bus_times)
#live_bus_times = []

print(" Stop 1 ")


for i in bus_times :
    print(i)
    #print("- OR -")
    #live_bus_times.append(datetime.fromtimestamp(i).strftime('%H:%M'))
    #print(datetime.fromtimestamp(i).strftime('%H:%M'))
b = len(bus_times)
bc = 0
if b == 0 :
    print("--:--")

print(" Stop 2 ")

#y = y + 87
if len(bus_times2) == 0:
    print("No live 2 bus times goten")
#print(bus_times)
live_bus_times2 = []

for i in bus_times2 :
    print(i)
    #print(datetime.utcfromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S'))
    #print("- OR -")
    #live_bus_times2.append(datetime.fromtimestamp(i).strftime('%H:%M'))
    #print(datetime.fromtimestamp(i).strftime('%H:%M'))
b2 = len(bus_times)
bc = 0
#y = y + 87


if b2 == 0 :
    print("--:--")
