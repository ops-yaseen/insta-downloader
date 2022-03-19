import os
import re
import tkinter.messagebox

import requests
import time
import datetime
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Style
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

CHROME_DRIVER = "drivers/chromedriver"
URL = 'https://www.instagram.com/accounts/login/'
DOWNLOAD_DIR = os.path.expanduser('~').replace('\\', '/') + '/Downloads/insta_my_saveds_videos'


class InstaBot:
    def __init__(self, user_name, user_password, chrome_driver_path):
        self.user_name = user_name
        self.user_password = user_password
        self.options = Options()
        self.options.headless = True
        self.browser = webdriver.Chrome(options=self.options, executable_path=chrome_driver_path)

    def login(self):
        self.browser.get(URL)
        self.browser.maximize_window()

        try:
            login_link = self.browser.find_element_by_xpath("//a[text()='Log in']")
            login_link.click()
        except NoSuchElementException:
            pass

        self.browser.implicitly_wait(time_to_wait=3)
        username_input = self.browser.find_element_by_css_selector("input[name='username']")
        password_input = self.browser.find_element_by_css_selector("input[name='password']")
        username_input.send_keys(self.user_name)
        password_input.send_keys(self.user_password)
        self.browser.implicitly_wait(time_to_wait=5)

        login_button = self.browser.find_element_by_xpath("//button[@type='submit']")
        login_button.click()
        self.browser.implicitly_wait(time_to_wait=5)

        if not self.options.headless:
            try:
                not_now = self.browser.find_element_by_css_selector(".cmbtv button")
            except NoSuchElementException as e:
                print(e)
            else:
                not_now.click()

            try:
                turn_off_notification = self.browser.find_element_by_xpath("//button[contains(text(), 'Not Now')]")
            except NoSuchElementException as e:
                print(e)
            else:
                turn_off_notification.click()
            self.browser.implicitly_wait(time_to_wait=3)

    def exit(self):
        self.browser.quit()

    def go_to_saved_items(self):
        try:
            click_profile = self.browser.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div['
                                                               '3]/div/div[6]/span')
        except NoSuchElementException:
            quit('Unable to go to profile')
            self.exit()
        else:
            click_profile.click()
            self.browser.implicitly_wait(time_to_wait=3)
        try:
            click_saved = self.browser.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div['
                                                             '3]/div/div[6]/div[2]/div[2]/div[2]/a[2]/div/div['
                                                             '2]/div/div/div/div')
        except NoSuchElementException:
            quit('Unable to go to saved items')
            self.exit()
        else:
            click_saved.click()

    @property
    def get_saved_link(self):
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        video_links = []
        while True:
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            links = []
            for element in self.browser.find_elements_by_class_name('_bz0w'):
                links.append(element.find_elements_by_tag_name('a'))
            for link in links:
                if len(link) != 0:
                    video_link = link[0].get_attribute('href')
                    video_links.append(video_link)

            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        return list(set(video_links))

    @staticmethod
    def calculate_time_taken(time_in_seconds):
        time_taken_split = str(datetime.timedelta(seconds=time_in_seconds)).split(':')
        hours = int(time_taken_split[0])
        minutes = int(time_taken_split[1])
        seconds = int(time_taken_split[2])
        if hours == 0 and minutes == 0:
            return f'{seconds} Seconds'
        elif hours == 0:
            return f'{minutes} Minutes, {seconds} Seconds'
        else:
            return f'{hours} Hours, {minutes} Minutes, {seconds} Seconds'

    def download_saved_videos(self):
        start_time = time.perf_counter()
        self.go_to_saved_items()
        videos = self.get_saved_link

        if not os.path.exists(DOWNLOAD_DIR):
            os.mkdir(DOWNLOAD_DIR)
        os.chdir(DOWNLOAD_DIR)

        for video in videos:
            self.browser.get(video)
            time.sleep(3)
            video_page_source = self.browser.page_source
            soup = BeautifulSoup(video_page_source, 'lxml')
            try:
                video_url = re.findall('"video_url":"([^"]+)"', video_page_source)[0].replace("\\u0026", "&")
            except IndexError:
                video_url = None
                page_scripts = soup.find_all('script')
                for script in page_scripts:
                    script_string = str(script)
                    if '.mp4?efg=' in script_string:
                        temp = script_string.split(',')
                        for element in temp:
                            if '.mp4?efg=' in element:
                                video_url = element.replace('"url":', '').strip('"').replace('\\u0026', '&')
                                break
            video_title = video_url.split('/')[-1].split('?')[0]
            r = requests.get(video_url)
            with open(video_title, 'wb') as video_file:
                video_file.write(r.content)

        end_time = time.perf_counter()
        time_taken_in_seconds = round(end_time - start_time)
        time_taken = self.calculate_time_taken(time_taken_in_seconds)
        tkinter.messagebox.showinfo(
            title="Done",
            message="Download Completed Successfully\n\n"
                    f"Total Time Taken : {time_taken}\n"
                    f"Total Videos Downloaded : {len(videos)}\n"
                    f"Videos downloaded path : {DOWNLOAD_DIR}"
        )


def main():
    user_name = user_name_box.get()
    user_password = user_password_box.get()
    if user_name == '' or user_password == '':
        tkinter.messagebox.showwarning(title='Warning!', message='UserID or Password Not Provided')
    else:
        user_password_box.delete(0, END)
        my_profile = InstaBot(user_name, user_password, CHROME_DRIVER)
        my_profile.login()
        my_profile.download_saved_videos()
        my_profile.exit()


def on_click(event):
    event.widget.delete(0, END)


def return_key(event):
    main()


window = Tk()
window.title("Instagram Downloader")
window.geometry("500x350")
window.configure(background='white', highlightthickness=True)
window.iconbitmap('images/insta-downloader-icon.ico')

canvas = Canvas(width=300, height=150, background='white', highlightthickness=False)
image = (Image.open('images/insta_logo.png'))
resized_image = image.resize((200, 100), Image.ANTIALIAS)
logo = ImageTk.PhotoImage(resized_image)
canvas.create_image(100, 0, image=logo, anchor="nw")
canvas.grid(column=0, row=0)

window.bind('<Return>', return_key)

user_name_label = Label(text="Email/UserName:", background='white')
user_name_label.grid(column=0, row=2)

password_label = Label(text="Password:", background='white')
password_label.grid(column=0, row=3)

user_name_box = ttk.Entry(width=30)
user_name_box.bind("<Button-1>", on_click)
user_name_box.grid(column=1, row=2, pady=10)
user_name_box.focus()
user_password_box = ttk.Entry(width=30, show='*')
user_password_box.bind("<Button-1>", on_click)
user_password_box.grid(column=1, row=3, pady=10)

style = Style()
style.map('TButton', foreground=[('active', '!disabled', 'green')],
          background=[('active', 'black')])
ui_login_button = ttk.Button(text='Login', command=main)
ui_login_button.grid(column=1, row=4)

# Disable window resize option by user
window.resizable(False, False)

window.mainloop()
