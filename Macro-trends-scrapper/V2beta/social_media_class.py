import threading
from concurrent.futures.thread import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
from yahoofinancials import YahooFinancials
from heapq import heappush, heappop
import datetime
import pytz
import concurrent.futures
import os
from functools import partial
from collections import deque
import smtplib, ssl
import yagmail
import getpass

class social_media_class():

    def __init__(self,password):
        self.password = password

    def send_gmail_message(self ,customer_mail,mail_contents):
    #https://blog.mailtrap.io/yagmail-tutorial/
        try:
            #initializing the server connection

            yag = yagmail.SMTP(user='wizardsofthemarket@gmail.com', password=self.password)
            #sending the email
            yag.send(to=customer_mail, subject='Buy alert!', contents=mail_contents)
            print("Email sent successfully")
        except:
            print("Error, email was not sent")



    def send_whatsapp_message(self, group_name, message_to_send):

        options = Options()
        options.add_argument('--profile-directory=Default')
        options.add_argument('--user-data-dir=C:/Temp/ChromeProfile')
        driver = webdriver.Chrome(chrome_options=options)

        driver.get("https://web.whatsapp.com/")
        wait = WebDriverWait(driver, 600)

        x_arg = '//span[contains(@title,' + group_name + ')]'
        group_title = wait.until(EC.presence_of_element_located((
            By.XPATH, x_arg)))
        print(group_title)
        print("Wait for few seconds")
        group_title.click()
        message = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')[0]

        message.send_keys(message_to_send)
        sendbutton = driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button')[0]
        sendbutton.click()
        driver.close()
