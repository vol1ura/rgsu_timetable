#!/usr/bin/env python
# Volodin Yuriy (volodinjuv@rgsu.net), 2020
# Parsing teacher's timetable on SDO.RSSU.NET
# ==================== Version 1.4 ===========================================
import csv
from datetime import datetime, timedelta
from getpass import getpass
from lxml.html import parse
import re
import requests


SDO_URL = 'https://sdo.rgsu.net'
AUTHORIZATION_URL = 'https://sdo.rgsu.net/index/authorization/role/guest/mode/view/name/Authorization'
TUTOR_URL = 'https://sdo.rgsu.net/switch/role/tutor'
WEEKDAYS = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6}

date = datetime.now()
while date.isoweekday() != WEEKDAYS['Понедельник']:
    date -= timedelta(1)

print("This program generate csv file with teacher's timetable for current or next week.")
print('If you choose n, timetable will be generated for next week.')
while True:
    w = input('Make timetable for current week (y/n)? ')
    if w.lower() == 'y' or w.lower() == 'д':
        TT_URL = SDO_URL + '/timetable/teacher'
        break
    elif w.lower() == 'n' or w.lower() == 'н':
        TT_URL = SDO_URL + '/timetable/teacher/index/week/next'
        date += timedelta(7)
        break
print('Input your login and password for sdo.rgsu.net:')
LOGIN = input('Login: ')
PASSWORD = getpass()

# Create payload
payload = {
    "start_login": 1,
    "login": LOGIN,
    "password": PASSWORD
}
# HTTP headers for sdo.rgsu.net
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': SDO_URL,
    'Connection': 'keep-alive',
    'Referer': 'https://sdo.rgsu.net/'}

# Perform login
sdo = requests.session()
request = sdo.post(AUTHORIZATION_URL, data=payload, headers=headers)
if request.ok and ('Пользователь успешно авторизован.' in request.text):
    print('Login OK!')
else:
    raise Exception('Login failed! May be incorrect login or password.')
# Tutor mode on
request = sdo.get(TUTOR_URL, headers=headers)
if request.ok:
    print('Tutor mode ON!')
# Scraping sdo
result = sdo.get(TT_URL, stream=True)
result.raw.decode_content = True
tree = parse(result.raw)
rows = tree.xpath('//tr[@class="tt-row"]')
lessons = list()
for row in rows:
    lesson = dict()
    cells = row.xpath('.//td/text()')
    lesson['st'] = cells[0][:5]
    lesson['ed'] = cells[0][8:13]
    lesson['cabinet'] = cells[1].strip()
    lesson['discipline'] = re.sub(r'(\d{2}.?){3},?', '', cells[2]).strip()
    lesson['d'] = ''.join([(w if len(w) == 1 else w[0].upper()) for w in re.split('[- ]', lesson['discipline'])])
    lesson['group'] = cells[3].strip()
    lesson['type'] = cells[4].strip()
    if lesson['type'] == 'лабораторная работа':
        lesson['stype'] = 'лаба'
    elif lesson['type'] == 'практическое занятие':
        lesson['stype'] = 'практика'
    else:
        lesson['stype'] = lesson['type']
    lesson['date'] = (date + timedelta(WEEKDAYS[cells[6].strip()] - 1)).strftime('%d.%m.%y')
    lessons.append(lesson)
i = 1
while i < len(lessons):
    if lessons[i]['date'] == lessons[i-1]['date'] and \
            lessons[i]['st'] == lessons[i-1]['st'] and lessons[i]['discipline'] == lessons[i-1]['discipline']:
        lessons[i]['cabinet'] += ' / ' + lessons[i-1]['cabinet']
        lessons[i]['group'] += ', ' + lessons[i-1]['group']
        del lessons[i-1]
        continue
    i += 1
timetable = list()
for lesson in lessons:
    timetable.append([lesson['date'], lesson['st'], lesson['date'], lesson['ed'], lesson['cabinet'],
                      lesson['group'] + ': ' + lesson['type'] + ', ' + lesson['discipline'],
                      lesson['d'] + ' ' + lesson['stype']])

f_name = 'calendar_' + date.strftime('%d_%m') + '.csv'
f = open(f_name, 'w', newline='', encoding='utf8')
with f:
    writer = csv.writer(f)
    writer.writerow(['Start Date', 'Start Time', 'End Date', 'End Time', 'Location', 'Description', 'Subject'])
    writer.writerows(timetable)
print(f'OK! Timetable was done - see file [{f_name}] in this directory.\nImport it to your Google Calendar.')
