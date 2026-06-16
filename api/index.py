# -*- coding: UTF-8 -*-
import requests
import re
from http.server import BaseHTTPRequestHandler
import json

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html',
    }
    gitpage = requests.get("https://github.com/users/" + name + "/contributions", headers=headers)
    data = gitpage.text

    pattern = re.compile(
        r'data-date="(\d{4}-\d{2}-\d{2})".*?class="sr-only position-absolute">(.*?)</tool-tip>',
        re.DOTALL
    )
    matches = pattern.findall(data)

    if not matches:
        return {"total": 0, "contributions": []}

    datalist = []
    for date_str, tooltip in matches:
        count_match = re.search(r'(\d+) contributions?', tooltip)
        count = int(count_match.group(1)) if count_match else 0
        datalist.append({"date": date_str, "count": count})

    datalist.sort(key=lambda x: x["date"])
    total = sum(item["count"] for item in datalist)
    datalistsplit = list_split(datalist, 7)

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
