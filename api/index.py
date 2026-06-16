# -*- coding: UTF-8 -*-
import requests
import re
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html',
    }
    gitpage = requests.get("https://github.com/users/" + name + "/contributions", headers=headers)
    data = gitpage.text

    date_pattern = re.compile(r'(\d+) contributions? on (\w+ \d+, \d{4})\.')
    no_contrib_pattern = re.compile(r'No contributions? on (\w+ \d+, \d{4})\.')

    contributions_map = {}

    for match in date_pattern.finditer(data):
        count = int(match.group(1))
        date_str = match.group(2)
        try:
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
            date_key = date_obj.strftime("%Y-%m-%d")
            contributions_map[date_key] = count
        except ValueError:
            continue

    for match in no_contrib_pattern.finditer(data):
        date_str = match.group(1)
        try:
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
            date_key = date_obj.strftime("%Y-%m-%d")
            if date_key not in contributions_map:
                contributions_map[date_key] = 0
        except ValueError:
            continue

    if not contributions_map:
        return {"total": 0, "contributions": []}

    sorted_dates = sorted(contributions_map.keys())
    first_date = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
    last_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")

    first_sunday = first_date - timedelta(days=first_date.weekday() + 1)
    if first_sunday > first_date:
        first_sunday -= timedelta(days=7)

    all_dates = []
    current = first_sunday
    while current <= last_date:
        date_key = current.strftime("%Y-%m-%d")
        all_dates.append({
            "date": date_key,
            "count": contributions_map.get(date_key, 0)
        })
        current += timedelta(days=1)

    total = sum(item["count"] for item in all_dates)
    datalistsplit = list_split(all_dates, 7)

    return {
        "total": total,
        "contributions": datalistsplit
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        spl = path.split('?')[1:]
        user = ""
        for kv in spl:
            parts = kv.split("=")
            if len(parts) == 2 and parts[0] == "user":
                user = parts[1]
                break
        data = getdata(user)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        return
