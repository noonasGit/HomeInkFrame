import requests
import configparser
import json
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class config_data:
    config_api_key: str
    config_project_id :str

@dataclass
class todo_data:
    content : str
    description : str
    is_completed : bool
    due_date : datetime
    is_recurring : bool

def gettodolist():
    config = get_config_data("todoist.ini")
    apikey = config.config_api_key
    projectID = config.config_project_id
    return_error = False
    #print("API "+apikey)
    #print("Project "+projectID)
    
    api_url = 'https://api.todoist.com/rest/v2/tasks?project_id='+projectID
    return_data: List[todo_data]

    api_headers = {}
    api_headers["Authorization"] = apikey
    api_headers["accept"] = "application/json"
    #print(api_headers)
    todo_return = []
    todo_return: list[todo_data]
    try:
        response = requests.get(api_url, headers=api_headers)
    except:
        return_error = True

    if return_error == False:
        Jtodos = response.json()
        cnt=0
        for J in Jtodos:
            content=J['content']
            description=J['description']
            is_completed=J['is_completed']
            try:
                date_str=J['due']['date']
                date_format = '%Y-%m-%d'
                due_date = datetime.strptime(date_str, date_format)
            except:
                due_date=False
            try:
                is_recurring=J['due']['is_recurring']
            except:
                is_recurring=False
            todo_return.append(todo_data(content=content,
                                         description=description,
                                         is_completed=is_completed,
                                         due_date=due_date,
                                         is_recurring=is_recurring))
            cnt +=1
            #print("Adding todo ,"+str(cnt))
    else:
        print("Error:", response.status_code, response.text)
        todo_return = []
    return todo_return

def getodolistbyduedate(date_due:datetime):
    config = get_config_data("todoist.ini")
    apikey = config.config_api_key
    projectID = config.config_project_id
    
    api_url = 'https://api.todoist.com/rest/v2/tasks?project_id='+projectID
    return_data: List[todo_data]
    daymonth = date_due.strftime("%d%m")

    api_headers = {}
    api_headers["Authorization"] = apikey
    api_headers["accept"] = "application/json"
    #print(api_headers)
    todo_return = []
    todo_return: list[todo_data]
    response = requests.get(api_url, headers=api_headers)
    if response.status_code == requests.codes.ok:
        Jtodos = response.json()
        cnt=0
        for J in Jtodos:
            content=J['content']
            description=J['description']
            is_completed=J['is_completed']
            try:
                date_str=J['due']['date']
                date_format = '%Y-%m-%d'
                due_date = datetime.strptime(date_str, date_format)
                due_daymonth = due_date.strftime("%d%m")
            except:
                due_date=False
            try:
                is_recurring=J['due']['is_recurring']
            except:
                is_recurring=False
            if due_date:
                if due_daymonth == daymonth:
                    todo_return.append(todo_data(content=content,
                                         description=description,
                                         is_completed=is_completed,
                                         due_date=due_date,
                                         is_recurring=is_recurring))
            cnt +=1
            #print("Adding todo ,"+str(cnt))
    else:
        print("Error:", response.status_code, response.text)
        todo_return = []
    return todo_return





def get_config_data(file_path:str):
    parser = configparser.ConfigParser()
    parser.read(file_path)
    data = dict()
    data['api-key-id'] = parser.get("config", "api-key")
    data['project-key-id'] = parser.get("config", "project-key")
    
    parser.clear
    r_data = config_data(config_api_key=data["api-key-id"], config_project_id=data["project-key-id"])
    return r_data
