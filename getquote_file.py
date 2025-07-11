# By Jonas Johansson
# For the KoboHUB Dashboard

from requests import get
from requests.exceptions import RequestException
from dataclasses import dataclass
import os
import random
import time

@dataclass
class quote_summary:
    quote_text: str
    quote_author :str


def quotefromfile(file_path:str):
    if os.path.exists(file_path) :
        quote_array = []
        with open(file_path) as my_file:
            for line in my_file:
                quote_array.append(line)
        #print(str(len(quote_array))+" quotes loaded...")
        ql = len(quote_array)
        qr_n = random.randint(0,(ql-1))
        quote_text = quote_array[qr_n].split("@")[0].replace('\n', '') + " "
        quote_author = quote_array[qr_n].split("@")[1].replace('\n', '') + " "
    else :
        quote_text = "No quote found"
        quote_author = "The Oracle"
    quote_data = quote_summary(quote_text, quote_author)
    return quote_data

