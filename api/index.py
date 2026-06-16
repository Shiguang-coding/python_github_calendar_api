# -*- coding: UTF-8 -*-
import requests
import re
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

def ordinal_to_int(s):
    return int(re.sub(r'(st|nd|rd|th)', '', s))

def getdata(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html',
    }
    gitpage = requests.get("https://github.com/users/" + name + "/contributions", headers=headers)
    data = gitpage.text

    today = datetime.utcnow()
    contributions_map = {}

    for match in re.finditer(r'(\d+) contributions? on ([A-Za-z]+ \d+\w*)\.', data):
        count = int(match.group(1))
        entry = match.group(2)
        m = re.match(r'([A-Za-z]+) (\d+\w*)', entry)
        if not m:
            continue
        month_str, day_str = m.group(1), m.group(2)
        day = ordinal_to_int(day_str)
        try:
            dt_no_year = datetime.strptime(f"{month_str} {day}", "%B %d")
        except ValueError:
            continue
        year = today.year
        dt = dt_no_year.replace(year=year)
        if dt > today + timedelta(days=1):
            dt = dt.replace(year=year - 1)
        contributions_map[dt.strftime("%Y-%m-%d")] = count

    if not contributions_map:
        return {"total": 0, "contributions": []}

    sorted_dates = sorted(contributions_map.keys())
    first_date = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
    last_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")

    first_sunday = first_date - timedelta(days=(first_date.weekday() + 1) % 7)

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
