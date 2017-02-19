#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
from app import models
import json
from bs4 import BeautifulSoup
import urllib.request
import datetime
import configparser
import os
from crontab import CronTab
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.request


URL_PARAMETER_PAGE = "&o="
CONFIG_FILE_PATH = "settings.ini"
PARAM_AUTOUPDATE = "config_autoupdate"

class Utils:

    @staticmethod
    def update_result_all(db_session, i_email=False):
        # Get the list of Searches
        searches = models.Search.query.all()
        for search in searches:
            Utils.update_result_url(db_session, i_search_name=search.name, i_url=search.url, i_id_search=search.id, i_max_price=search.price_max, \
                                                 i_min_price=search.price_min, i_email=search.email)
        return

    @staticmethod
    def update_result_url(db_session, i_search_name:str, i_url:str, i_id_search:int, i_max_price=999999, i_min_price=0, i_max_page_nb=5, i_email=False):
        old_results = models.Results.query.join(models.Search, models.Search.id == models.Results.id_search)\
            .filter(models.Search.name == i_search_name).all()
        new_results = Utils.find_results_url(i_url=i_url, i_id_search=i_id_search, i_max_price=i_max_price, i_min_price=i_min_price, i_max_page_nb=i_max_page_nb)
        # create a list of id's:
        ids = []
        #Determine the last date from the previous searches
        res_list = []
        if len(old_results) > 0:
            last_date = old_results[0].date
        else:
            last_date = datetime.date.min

        for res in old_results:
            ids.append(res.lbc_id)
        for res in new_results:
            if res.date < last_date:
                break
            if not res.lbc_id in ids:
                # add new result to DB
                db_session.add(res)
                res_list.append(res)
        db_session.commit()
        if i_email:
            print("Email sent to " + i_email + " for " + i_search_name)
            Utils.send_result_by_email(i_results=res_list, i_email=i_email, i_title=i_search_name)


    @staticmethod
    def send_result_by_email(i_results:[], i_email:str, i_title:str):
        if len(i_results) != 0:
            # Open a plain text file for reading.  For this example, assume that
            # the text file contains only ASCII characters.
            msg = MIMEMultipart('alternative')

            # me = 'btdummyemailbox@gmail.com'
            me = 'sorc0012@alwaysdata.net'
            you = i_email
            msg['Subject'] = str(len(i_results)) + ' nouveaux resultats pour ' + i_title
            msg['From'] = me
            msg['To'] = you

            text = str(len(i_results)) + ' nouveaux resultats pour ' + i_title + "</br>"

            #############
            # FORMAT HTML EMAIL BODY
            #############
            html = Utils.get_results_html(i_results)

            # Record the MIME types of both parts - text/plain and text/html.
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(part1)
            msg.attach(part2)

            # Send the message via local SMTP server.
            server = smtplib.SMTP('smtp-sorc0012.alwaysdata.net', 587)
            # server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            # server.login(me, "btdummyemail")
            server.login(me, "alwaysemail12")
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            server.sendmail(me, you, msg.as_string())
            server.quit()

            return

    @staticmethod
    def find_results_url(i_url:str, i_id_search:int, i_max_price=999999, i_min_price=0, i_max_page_nb=5):
        res_list = []
        pagenb = 1
        if URL_PARAMETER_PAGE not in i_url:
            i_url += URL_PARAMETER_PAGE + '1'
        while pagenb < i_max_page_nb:
            url = re.sub('(&o=\d)', URL_PARAMETER_PAGE + str(pagenb), i_url)
            pagenb += 1
            print("Searching: " + url)
            html = urllib.request.urlopen(url)
            soup = BeautifulSoup(html, "lxml")
            list_ads = soup.find(class_='tabsContent block-white dontSwitch')
            # get list element
            try:
                ul = list_ads.find('ul')
            except AttributeError:
                #exit if no list of result found
                break
            for li in ul.find_all('li'):
                ad = models.Results()
                ad.id_search = i_id_search
                # get element link
                link = li.find("a")
                ad.url = link.get("href")

                # get ad Id
                try:
                    datainfo = json.loads(link.get("data-info"))
                    ad.lbc_id = int(datainfo["ad_listid"])
                except:
                    ad.lbc_id = 0

                # <h2 class="item_title">
                ad.title = link.get("title")

                # Price
                try:
                    price = int(li.select('h3[itemprop=price]')[0]['content'])
                    if i_max_price or i_min_price:
                        if price < int(i_min_price) or price > int(i_max_price):
                            continue
                except:
                    price = 0
                ad.price = price

                # Date
                try:
                    date_str = li.select('p[itemprop=availabilityStarts]')[0]['content']
                    date_list = date_str.split('-')
                    date = datetime.date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
                except:
                    date = datetime.date.today()
                ad.date = date

                # Img link
                span = link.find_all("span")
                try:
                    ad.img_url = span[1].get("data-imgsrc")
                except:
                    ad.img_url = ''
                if ad.img_url is None:
                    ad.img_url = ''

                res_list.append(ad)
        return res_list

    @staticmethod
    def create_config_file():
        """
        Create a config file
        """
        config = configparser.ConfigParser()
        config.add_section("SETTINGS")
        config.set("SETTINGS", "AutoConfig", str(False))

        with open(CONFIG_FILE_PATH, "w") as config_file:
            config.write(config_file)

    @staticmethod
    def getConfig_from_file():
        """
        Read config file
        :return: Dictionary
        """
        parser = configparser.ConfigParser()
        try:
            parser.read(CONFIG_FILE_PATH)
            config = {}
            for key, val in parser.items("SETTINGS"):
                if val == 'True':
                    val = True
                elif val == 'False':
                    val = False
                config[key] = val
        except:
            Utils.create_config_file()
            config = {}
        return config

    @staticmethod
    def save_config_file(i_config:dict):
        """
        Save config file
        :return: Boolean
        """
        config = configparser.ConfigParser()
        config.add_section("SETTINGS")
        for elem in i_config:
            config.set("SETTINGS", elem, str(i_config[elem]))
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config.write(config_file)
        return True

    @staticmethod
    def delete_job():
        cron = CronTab(user=True)
        list = cron.find_comment('ALERTBONCOIN')
        for job in list:
            print(job)
            job.clear()
            cron.remove(job)

    @staticmethod
    def add_job():
        cron = CronTab(user=True)
        self.delete_job()
        cwd = os.getcwd()
        cron_job = cron.new(command= 'python3 ' + cwd +'/ABC_monitor.py', comment='ALERTBONCOIN')
        cron_job.minute.on(0)
        cron_job.hour.during(0, 23)
        cron_job.enable()
        self.cron.write()

    @staticmethod
    def get_results_html(new_res: []):
        content = ''
        for result in new_res:
            line = "<tr> " + "<td><img src=\"https:" + str(result.img_url) + "\"></td>" \
                   + "<td><a href=\"https:" + str(result.url) + "\">" + str(result.title) + "</a></td>" \
                   + "<td>" + str(result.price) + "</td>" \
                   + "<td>" + str(result.date) + "</td>"
            content += line

        # Create the body of the message (a plain-text and an HTML version).
        html = """<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
<link rel="stylesheet" href="https://code.getmdl.io/1.2.1/material.indigo-pink.min.css">
<script defer src="https://code.getmdl.io/1.2.1/material.min.js"></script>
</head>
<body>
<table border="1px solid black" class="mdl-data-table mdl-js-data-table"><tr>
                                    <th>Image</th>
                                    <th class="mdl-data-table__cell--non-numeric">Titre</th>
                                    <th class="">Prix</th>
                                    <th class="">Date</th>
                                </tr>
                            %s
                            </table>
                        </body>
                    </html>
                    """ % (content)
        return html