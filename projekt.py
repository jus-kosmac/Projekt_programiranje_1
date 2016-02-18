import requests
import re
import os
import csv
import pandas as pd

def shrani(url, datoteka):
    if os.path.isfile(datoteka):
        print('Shranjeno ze od prej:' + datoteka)
        return
    pripravi_imenik(datoteka)
    r = requests.get(url)
    with open(datoteka, 'w', encoding='utf-8') as f:
        f.write(r.text)
        print('Shranil si:' + datoteka)

def preberi(datoteka):
    with open(datoteka, encoding='utf-8') as f:
        vsebina = f.read()
    return vsebina

def pripravi_imenik(ime_datoteke):
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)

def zapisi_tabelo(slovarji, imena_polj, ime_datoteke):
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w') as csv_dat:
        writer = csv.DictWriter(csv_dat, fieldnames=imena_polj)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)

def popravi_datum(datum):
    seznam = datum.split()
    seznam[1] = seznam[1][:-3]
    return pd.to_datetime(''.join(seznam), format="%b%d%Y").date()

def zajemi_vsebino():
    shrani('http://socialblade.com/youtube/top', 'top.html')
    regex_kategorija = re.compile(r'<a href="/youtube/top/category/(?P<kategorija>.*?)">.*?</a></div>',
                                  flags=re.DOTALL)
    for ujemanje in re.finditer(regex_kategorija, preberi('top.html')):
        kat = ujemanje.group('kategorija')
        url = 'http://socialblade.com/youtube/top/category/' + kat
        ime = kat + '.html'
        shrani(url, ime)
        regex_kanala = re.compile(r'<a href="/youtube/user/(?P<channel>.*?)">.*?</a>',
                                  flags=re.DOTALL)
        kanali = list(re.finditer(regex_kanala, preberi(ime)))
        for kanal in kanali[:100]:
            user = kanal.group('channel')
            url_novi = 'http://socialblade.com/youtube/user/' + user
            ime_novo = '{}/{}.html'.format(kat, user)
            shrani(url_novi, ime_novo)

zajemi_vsebino()

def podatki():
    regex_kanala = re.compile(r'Uploads</span><br/>.*?>(?P<uploads>.*?)</span>.*?'
                              r'Subscribers</span><br/>.*?>(?P<subs>.*?)</span>.*?'
                              r'Video Views</span><br/>.*?>(?P<views>.*?)</span>.*?'
                              r'Country</span><br/>.*?youtube/top/country/(?P<country>.*?)">.*?'
                              r'User Created</span><br/>.*?>(?P<date>.*?)</span>',
                              flags=re.DOTALL)
    seznam_slovarjev = []
    
    for mapa in list(os.walk('.'))[0][1]:
        seznam_datotek = os.listdir(os.path.join('.', mapa))
        for dat in seznam_datotek:
            datoteka = os.path.join(mapa, dat)
            for ujemanje in re.finditer(regex_kanala, preberi(datoteka)):
                slovar = ujemanje.groupdict()
                slovar['date'] = popravi_datum(slovar['date'])
                slovar['user'] = dat[:-5]
                slovar['type'] = mapa
                seznam_slovarjev.append(slovar)

    zapisi_tabelo(seznam_slovarjev, ['user', 'type', 'date', 'country', 'uploads', 'views', 'subs'], 'podatki.csv')

podatki()
    














