# Volodin Yuriy, 2020
# volodinjuv@rgsu.net
# Parsing teacher's timetable on SDO.RSSU.NET
# ===========================================
# We use lxml parser, install it if you need: pip3 install lxml
# Also we use next modules
from bs4 import BeautifulSoup # Install it if you need: pip3 install beatifulsoup
import csv                    # Install it if you need: pip3 install csv
from datetime import datetime, timedelta
import locale
import re
import requests               # Install it if you need: pip3 install requests
import time

locale.setlocale(locale.LC_ALL, "")

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

begin_date = datetime.now()
while begin_date.strftime("%A") != "понедельник":
    begin_date -= timedelta(1)
print('Begin of week: ', begin_date.strftime("%d/%m/%Y (%A)")) # begin of week
end_date = begin_date + timedelta(14) # end of two week interval 

dates2w = []
for i in range(13):
    dates2w.append((begin_date + timedelta(i)).strftime("%d.%m.%y"))

if "Нечетная неделя" == soup.find('div', class_="panel-green").find('p', class_="heading").text:
    odd_week = True
print('This week is odd: ', odd_week)    
print('Working days selected interval:')
print(dates2w)

data = []
for tr in trs[1:]:
    cells = tr.find_all('td')
    p = re.compile(r'\d{2}\.\d{2}\.\d{2}')
    dates = p.findall(cells[3].text)
    dates = list(set(dates2w).intersection(set(dates)))
    if len(dates) > 0:
        p = re.compile(r'[а-яА-ЯёЁ" "-]+')
        discipline = p.findall(cells[3].text)[0].strip()
        if len(discipline) > 16:
            discipline_s = ''.join([(w if len(w) == 1 else w[0].upper()) for w in discipline.split(' ')])
        else:
            discipline_s = discipline
        lesson_type = cells[4].text.strip()
        if lesson_type.lower() == 'лабораторная работа':
            lesson_type_s = 'лаба'
        elif lesson_type.lower() == 'практическое занятие':
            lesson_type_s = 'практика'
        else:
            lesson_type_s = lesson_type
        location = cells[5].text.strip()
        group = cells[6].text.strip()
        p = re.compile(r'\d+')
        hmhm = p.findall(cells[1].text.strip())
        lesson_time = ['', '']
        try:
            for i in range(2):
                lesson_time[i] += hmhm[2*i]+':'+hmhm[1 + 2*i]
        except:
            print('Something went wrong!!! Bad time format: [ {} ]'.format(cells[1].text))
            print('See timetable and manually correct time for:', cells[0].text, cells[2].text, group)
            lesson_time = ['8:15', '22:05']
            
        for date in dates:
            data.append([date, lesson_time[0], date, lesson_time[1],\
                         location, group + ': ' + discipline + ', ' + lesson_type, \
                         discipline_s + ' ' + lesson_type_s])

today = time.strftime('%d.%m')
f = open('calendar_'+today+'.csv', 'w', newline='', encoding='utf8')
with f:
    writer = csv.writer(f)
    writer.writerow(['Start Date', 'Start Time', 'End Date', 'End Time', 'Location', 'Description','Subject'])
    writer.writerows(data)



    

