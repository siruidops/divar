#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import time
import datetime as dt
import sys
import os
import threading
from stem import Signal
from stem.control import Controller
from openpyxl import load_workbook
from openpyxl import Workbook

city_list = ['https://divar.ir/s/tehran', 'https://divar.ir/s/mashhad', 'https://divar.ir/s/isfahan', 'https://divar.ir/s/karaj', 'https://divar.ir/s/shiraz', 'https://divar.ir/s/tabriz', 'https://divar.ir/s/qom', 'https://divar.ir/s/ahvaz', 'https://divar.ir/s/kermanshah', 'https://divar.ir/s/urmia']
id_list = []

lock1 = threading.Lock()
lock2 = threading.Lock()
lock3 = threading.Lock()

datenow = dt.datetime.now()
year = datenow.year; month = datenow.month; day = datenow.day
timenow = "{}_{}_{}".format(year,month,day)

l = []

iden_status = 0


if not os.path.isfile('divar-car-{}.xlsx'.format(timenow)):
    workbook_car = Workbook()
    sh_car = workbook_car.active
    sh_car['A1'] = 'ID'
    sh_car['B1'] = 'Group'
    sh_car['C1'] = 'Title'; sh_car.column_dimensions['C'].width = 30
    sh_car['D1'] = 'Url'
    sh_car['E1'] = 'Location'
    sh_car['F1'] = 'Production year'
    sh_car['G1'] = 'Model'
    sh_car['H1'] = 'Kilometre'
    sh_car['I1'] = 'Color'
    sh_car['J1'] = 'Gearbox'
    sh_car['K1'] = 'Body'
    sh_car['L1'] = 'Description'; sh_car.column_dimensions['L'].width = 70
    sh_car['M1'] = 'Phone'; sh_car.column_dimensions['M'].width = 18
    sh_car['N1'] = 'Price'; sh_car.column_dimensions['N'].width = 15 #ok
    sh_car['O1'] = 'Date'
    sh_car['P1'] = 'Pictures'

else:
    workbook_car = load_workbook('divar-car-{}.xlsx'.format(timenow))
    sh_car = workbook_car.worksheets[0]
    for i in range(2, sh_car.max_row+1):
        id_list.append(sh_car.cell(row=i, column=1).value.strip())



if not os.path.isfile('divar-motor-{}.xlsx'.format(timenow)):
    workbook_motor = Workbook()
    sh_motor = workbook_motor.active
    sh_motor['A1'] = 'ID'
    sh_motor['B1'] = 'Group'
    sh_motor['C1'] = 'Title'; sh_motor.column_dimensions['C'].width = 30
    sh_motor['D1'] = 'Url'
    sh_motor['E1'] = 'Location'
    sh_motor['F1'] = 'Production year'
    sh_motor['G1'] = 'Model'
    sh_motor['H1'] = 'Kilometre'
    sh_motor['I1'] = 'Description'; sh_motor.column_dimensions['I'].width = 70
    sh_motor['J1'] = 'Phone'; sh_motor.column_dimensions['J'].width = 18
    sh_motor['K1'] = 'Price'; sh_motor.column_dimensions['K'].width = 15
    sh_motor['L1'] = 'Date'
    sh_motor['M1'] = 'Pictures'

else:
    workbook_motor = load_workbook('divar-motor-{}.xlsx'.format(timenow))
    sh_motor = workbook_motor.worksheets[0]
    for i in range(2, sh_motor.max_row+1):
        id_list.append(sh_motor.cell(row=i, column=1).value.strip())


if not os.path.isfile('divar-{}.xlsx'.format(timenow)):
    workbook = Workbook()
    sh = workbook.active
    sh['A1'] = 'ID'
    sh['B1'] = 'Group'
    sh['C1'] = 'Title'; sh.column_dimensions['C'].width = 30
    sh['D1'] = 'Url'
    sh['E1'] = 'Location'
    sh['F1'] = 'Description'; sh.column_dimensions['F'].width = 70
    sh['G1'] = 'Phone'; sh.column_dimensions['G'].width = 30
    sh['H1'] = 'Price'; sh.column_dimensions['H'].width = 20
    sh['I1'] = 'Date'
    sh['J1'] = 'Pictures'

else:
    workbook = load_workbook('divar-{}.xlsx'.format(timenow))
    sh = workbook.worksheets[0]
    for i in range(2, sh.max_row+1):
        id_list.append(sh.cell(row=i, column=1).value.strip())



def iden_():
    global iden_status
    if not iden_status:
        iden_status = 1
        control_port = 9051
        with Controller.from_port(port=control_port) as controller:
            controller.authenticate()
            time.sleep(controller.get_newnym_wait())
            controller.signal(Signal.NEWNYM)
        iden_status = 0



def runner():

    url = city_list.pop()
    r = requests.Session()
    r.headers = {'Connection': "close", "Accept": "*/*", "Content-type": "application/x-www-form-urlencoded; charset=UTF-8", "Accept-Language": "en-US", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    while 1:
        url_status_re = 0
        for i in range(1,51):
            if url_status_re == 1:
                break

            rr = r.get("{}/?page={}".format(url,str(i)))
            source_html = rr.text
            bs = BeautifulSoup(source_html, 'html.parser')
            urls_ = []

            for i in bs.find_all('a', {'class':"col-xs-12 col-sm-6 col-xl-4 p-tb-large p-lr-gutter post-card"}):
                urls_.append(i['href'])

            for lurl in urls_:
                id_ = lurl.split('/')[-1]

                if id_ in id_list:
                    url_status_re = 1
                    continue
                else:
                    id_list.append(id_)
                    url_status_re = 0

                r_ = r.get("https://divar.ir"+lurl)
                html_source = r_.text
                bs_ = BeautifulSoup(html_source, 'html.parser')
                title = "|". join(bs_.find('title').text.split('|')[0:-1]).strip()
                images = bs_.find_all('img', {"class":'image-slider'})
                pictures = []

                for image in images:
                    pictures.append(image['src'])

                pictures = " , ".join(pictures)
                try:
                    publish_time = bs_.find("span", {'class':"post-header__publish-time"}).text.strip()
                except:
                    continue

                group = ' '
                location = ' '
                type_ = ' '
                price = ' '
                zz = bs_.find_all("div", {'class':"post-fields-item"})
                cc = []
                
                for i in zz:
                    cd = i.find_all("span", {'class':"post-fields-item__title"})
                    for j in cd:
                        cc.append(j)

                for i in cc:
                    if i.text=='دسته‌بندی':
                        group = i.find_next().text.strip()
                    elif i.text=='محل':
                        location = i.find_next().text.strip()
                    elif i.text=='نوع آگهی':
                        type_ = i.find_next().text.strip()
                    elif i.text=='قیمت' or i.text=='قیمت کل':
                        price = i.find_next().text.strip()
                    else:
                        pass

                try:
                    description = bs_.find('div', {'class':"post-page__description"}).text.strip()
                except:
                    description = ' '

                success = 0
                while not success:
                    try:
                        phone_number = requests.get('https://api.divar.ir/v5/posts/{}/contact/'.format(id_), proxies={'http':"socks5://localhost:9050",'https':"socks5://localhost:9050"}).json()['widgets']['contact']['phone']
                        success = 1
                    except:
                        iden_()
                        success = 0


                berand = ' '
                year_ = ' '
                kilometre = ' '
                badane = ' '
                color = ' '
                gearbox = ' '
                forosh = ' '
                sanad = ' '

                if "سواری" == group or "سنگین" == group:
                    for i in cc:
                        if i.text == 'برند':
                            berand = i.find_next().text.strip()
                        elif i.text == 'سال ساخت':
                            year_ = i.find_next().text.strip()
                        elif i.text == 'کارکرد':
                            kilometre = i.find_next().text.strip()
                        elif i.text == 'وضعیت بدنه':
                            badane = i.find_next().text.strip()
                        elif i.text == 'رنگ':
                            color = i.find_next().text.strip()
                        elif i.text == 'گیربکس':
                            gearbox = i.find_next().text.strip()
                        elif i.text == 'نحوه فروش':
                            forosh = i.find_next().text.strip()
                        elif i.text == 'سند':
                            sanad = i.find_next().text.strip()
                        else:
                            pass

                    expens = [id_, group, title, "https://divar.ir"+lurl, location, year_, berand, kilometre, color, gearbox, badane, description, phone_number, price, publish_time, pictures]
                    sh_car.append(expens)
                    workbook_car.save('divar-car-{}.xlsx'.format(timenow))

                elif 'موتورسیکلت' in group:
                    for i in cc:
                        if i.text == 'برند':
                            berand = i.find_next().text.strip()
                        elif i.text == 'سال ساخت':
                            year_ = i.find_next().text.strip()
                        elif i.text == 'کارکرد':
                            kilometre = i.find_next().text.strip()
                        else:
                            pass

                    expens = [id_, group, title, "https://divar.ir"+lurl, location, year_, berand, kilometre, description, phone_number, price, publish_time, pictures]
                    sh_motor.append(expens)
                    workbook_motor.save('divar-motor-{}.xlsx'.format(timenow))

                else:
                    expens = [id_, group, title, "https://divar.ir"+lurl, location, description, phone_number, price, publish_time, pictures]
                    sh.append(expens)
                    workbook.save('divar-{}.xlsx'.format(timenow))

        time.sleep(21600)


class myThread(threading.Thread):
	def __init__(self, threadID, name, counter, lock1, lock2, lock3):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.lock1 = lock1
		self.lock2 = lock2
		self.lock3 = lock3

	def run(self):
		runner()

if __name__ == "__main__":
    attack_threads = []

    for i in range(10):
        attack_threads.append(myThread(i, "Thread-{}".format(i), i, lock1, lock2, lock3))
        attack_threads[i].start()

    for i in range(10):
        attack_threads[i].join()
