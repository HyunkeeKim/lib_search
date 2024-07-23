import requests
import json
import pathlib

def send_message_to_slack(text, send_url):
    payload = { "text" : text }
    requests.post(send_url, json=payload)

def store_file(results, filename):
    p = pathlib.Path(__file__).with_name(filename)
    with p.open('w') as json_file:
        json.dump(results, json_file, indent=4)

def read_file(filename):
    try:
        p = pathlib.Path(__file__).with_name(filename)
        with p.open('r') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return
