from todoist import gettodolist, getodolistbyduedate
import requests
import configparser
import json
from dataclasses import dataclass
from datetime import datetime
from typing import List

print("Getting doday's todos...")
today_todo_list = getodolistbyduedate(datetime.now())
numtodos = len(today_todo_list)
print("Got "+str(numtodos)+" todos...")

print("Getting all todos...")
all_todo_list = gettodolist()
allnumtodos = len(all_todo_list)
print("Got "+str(allnumtodos)+" todos...")

tnum = 0
tdrow = 0
col_space = 0

if numtodos > 0:
    can_show_quote = False
    print("Todoist feature" ,"geting todoist list...")

    today_todo_list.sort(key=lambda x: x.due_date, reverse=True) # Sort by Due date
    for tsk in today_todo_list:
        tsk_title = tsk.content.replace('\n', '')
        print(tsk_title)
    daymonth = datetime.today().strftime("%d%m")

    today_todo_list.sort(key=lambda x: x.due_date, reverse=True) # Sort by Due date
    for tsk in today_todo_list:
        tsk_title = tsk.content.replace('\n', '')
        #print(tsk_title)

else:
    can_show_quote = True
