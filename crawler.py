# Volodin Yuriy, 2020
# volodinjuv@rgsu.net
# Parsing teacher's timetable on SDO.RSSU.NET
# ===========================================
# We use lxml parser, install it if you need: pip3 install lxml
# Also we use next modules
from bs4 import BeautifulSoup # Install it if you need: pip3 install beatifulsoup
import csv
import re
import requests               # Install it if you need: pip3 install requests
import time

teacher = 'Володин+Юрий+Владимирович' # use + instead of space

def get_html(url):
    r = requests.get(url) # Response
    if r.status_code != 200:
        print("Can't get page. Check connection to rgsu.net and try to restart this script.")
    return r.text # Return html page code

rssu_url = 'https://rgsu.net/for-students/timetable/timetable.html?template=&action=index&admin_mode=&nc_ctpl=935&Teacher=' # Calendar on current week
rssu_url += teacher 
html = get_html(rssu_url)

soup = BeautifulSoup(html, 'lxml')

trs = soup.find('div', class_="row collapse").find_all('tr')
print(trs[1:4])
today = time.strftime('%d.%m')
f = open('calendar_'+today+'.csv', 'w')
with f:
    writer = csv.writer(f)
    writer.writerow(['Start Date', 'Start Time', 'End Date', 'End Time', 'Location', 'Description','Subject'])

data = []
for tr in trs[1:4]:
    cells = tr.find_all('td')
    data.append(cells)
    print(cells[1].get_text())

p = re.compile(r'\d+')
print(p.findall('12 drummers drumming, 11 pipers piping, 10 lords a-leaping'))

    

