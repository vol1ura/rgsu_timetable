#!/usr/bin/env python3
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
import sys, time

locale.setlocale(locale.LC_ALL, "")

try:
    f = open('settings.txt', encoding='utf8')
    try:
        teacher = '+'.join(f.readline().strip().split(' '))
        date_line = list(map(int, f.readline().strip().split('.')))
        begin_date = datetime(date_line[2], date_line[1], date_line[0])
        date_line = list(map(int, f.readline().strip().split('.')))
        end_date = datetime(date_line[2], date_line[1], date_line[0])
    except Exception as e:
        print(e)
        teacher = 'Володин+Юрий+Владимирович'
        begin_date = datetime.now()
        end_date = datetime.now()
        print('Error!!! Check correctness of template!')
        print('I will use default settings...')
    finally:
        f.close()
except(IOError, OSError) as e:
    print(e)
    print()
    sys.exit('Error when reading settings.txt !!! Check also file encoding.')
    
def get_html(url):
    r = requests.get(url) # Response
    if r.status_code != 200:
        print("Can't get page. Check connection to rgsu.net and try to restart this script.")
    return r.text # Return html page code

rssu_url = 'https://rgsu.net/for-students/timetable/timetable.html?template=&action=index&admin_mode=&nc_ctpl=935&Teacher='
rssu_url += teacher 
html = get_html(rssu_url)

soup = BeautifulSoup(html, 'lxml')

trs = soup.find('div', class_="row collapse").find_all('tr')

# ----- Diagnostic messages --------------------
date_now = datetime.now()
while date_now.strftime("%A") != "понедельник":
    date_now -= timedelta(1)
print('Begin of current week: ', date_now.strftime("%d/%m/%Y (%A)")) # begin of week
# Sunday belongs to next week on this site
#oddness = 
if "Нечетная неделя" == soup.find('div', class_="panel-green").find('p', class_="heading").text:
    odd_week = True
else:
    odd_week = False
if datetime.now().isoweekday() == 7:
    odd_week = not odd_week
print('This week is odd: ', odd_week)    
# -----------------------------------------------

date_sett = []
while(begin_date <= end_date):
    date_sett.append(begin_date.strftime("%d.%m.%y"))
    begin_date += timedelta(1)
#print('Days in selected interval:')
#print(date_sett)

data = []
for tr in trs[1:]:
    cells = tr.find_all('td')
    p = re.compile(r'\d{2}\.\d{2}\.\d{2}')
    dates = p.findall(cells[3].text)
    dates = list(set(date_sett).intersection(set(dates)))
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
            print('Bad time format: [ {} ]'.format(cells[1].text))
            print('See timetable and manually correct time for:', cells[0].text, cells[2].text, group)
            lesson_time = ['8:00', '22:00']
            
        for date in dates:
            data.append([date, lesson_time[0], lesson_time[1],\
                         location, group, discipline, lesson_type, \
                         discipline_s + ' ' + lesson_type_s])
    
datalines = []
for i in range(len(data)):
    j = i + 1
    while(j < len(data)):
        if data[i][0] == data[j][0] and data[i][1] == data[j][1] and data[i][7] == data[j][7]:
            if data[i][3] != data[j][3]:
                data[j][3] += ' / ' + data[i][3]
            data[j][4] += ', ' + data[i][4]
            break
        j += 1
    else:
        datalines.append([data[i][0], data[i][1], data[i][0], data[i][2], data[i][3], \
                          data[i][4] + ': ' + data[i][5] + ', ' + data[i][6], data[i][7]])

print('Load in selected period equals {0} hours. It is {1:.1f} hours per week in average.'.format(2 * len(datalines), 7 * 2 * len(datalines) / max(1, len(date_sett))))

f_name = 'calendar_' + time.strftime('%d.%m') + '.csv'
f = open(f_name, 'w', newline='', encoding='utf8')
with f:
    writer = csv.writer(f)
    writer.writerow(['Start Date', 'Start Time', 'End Date', 'End Time', 'Location', 'Description','Subject'])
    writer.writerows(datalines)
print('================================================================================')
print('OK! Timetible was done - see file [' + f_name + '] in this directory.\
\nImport it to your Google Calendar.')
