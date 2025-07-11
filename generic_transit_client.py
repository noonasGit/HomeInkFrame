from datetime import date, time, datetime 
import time
from generic_transit import next_transit

#Bus schedule

b = 0


bus_times = []
print("Stop 1")

bus_times = next_transit(1)
b = len(bus_times)
bc = 0

if b > 0 :
    print(str(b)+" departure schedules remaining")
    while bc < 3 :
        print(bus_times[bc])
        bc = bc +1
if b == 0 :
    print("--:--")

print("Stop 2")

bus_times = next_transit(2)
b = len(bus_times)
bc = 0

if b > 0 :
    print(str(b)+" departure schedules remaining")
    while bc < 3 :
        print(bus_times[bc])
        bc = bc +1
if b == 0 :
    print("--:--")
