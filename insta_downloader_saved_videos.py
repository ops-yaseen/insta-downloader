import os
import re
import numpy
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
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

CHROME_DRIVER = "drivers/chromedriver"
FF_DRIVER = 'drivers/geckodriver'
URL = 'https://www.instagram.com/accounts/login/'
EMAIL_ID = 'wolverinelog7@gmail.com'
DOWNLOAD_DIR = os.path.expanduser('~').replace('\\', '/') + '/Videos/temp_dir'


class InstaBot:
    def __init__(self, user_name, user_password, driver_path):
        self.user_name = user_name
        self.user_password = user_password
        self.options = Options()
        self.options.headless = False
        # self.browser = webdriver.Chrome(options=self.options, executable_path=driver_path)
        self.browser = webdriver.Firefox(options=self.options, executable_path=driver_path)

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

    # def go_to_saved_items(self):
    #     try:
    #         # click_profile = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div['
    #         #                                                    '1]/div[1]/section/nav/div[2]/div/div/div[2]/div/div['
    #         #                                                    '6]/div[1]/span/img')
    #         click_profile = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div['
    #                                                            '1]/section/nav/div[2]/div/div/div[2]/div/div[6]/div['
    #                                                            '1]/span/img')
    #
    #     except NoSuchElementException:
    #         quit('Unable to go to profile')
    #         self.exit()
    #     else:
    #         click_profile.click()
    #         self.browser.implicitly_wait(time_to_wait=3)
    #     try:
    #         # click_saved = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div['
    #         #                                                  '1]/div[1]/section/nav/div[2]/div/div/div[2]/div/div['
    #         #                                                  '6]/div[2]/div[2]/div[2]/a[2]/div/div[2]/div/div/div/div')
    #         click_saved = self.browser.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div['
    #                                                          '1]/section/nav/div[2]/div/div/div[2]/div/div[6]/div['
    #                                                          '2]/div/div[2]/div[2]/a/div/div[2]/div/div/div/div')
    #     except NoSuchElementException:
    #         quit('Unable to go to saved items')
    #         self.exit()
    #     else:
    #         click_saved.click()
    #     try:
    #         self.browser.get('https://www.instagram.com/wollog8/saved/all-posts/')
    #     except NoSuchElementException:
    #         quit('Unable to go to all saved posts')

    @property
    def get_saved_link(self):
        time.sleep(8)
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        video_links = []
        while True:
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.browser.implicitly_wait(4)
            time.sleep(2)
            links = []
            for element in self.browser.find_elements_by_class_name('_aanf'):
                links.append(element.find_elements_by_tag_name('a'))
            for link in links:
                if len(link) != 0:
                    video_link = link[0].get_attribute('href')
                    video_links.append(video_link)

            self.browser.implicitly_wait(4)
            time.sleep(3)
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
        self.browser.get('https://www.instagram.com/wollog8/saved/all-posts/')
        # self.go_to_saved_items()
        videos = self.get_saved_link

        if not os.path.exists(DOWNLOAD_DIR):
            os.mkdir(DOWNLOAD_DIR)
        os.chdir(DOWNLOAD_DIR)

        with open('vid_links.txt', 'a') as file:
            for video in videos:
                file.write(video + '\n')

        for video in videos:
            video = video.replace('/p/', '/reel/')
            self.browser.get(video)
            time.sleep(3)
            video_page_source = self.browser.page_source
            soup = BeautifulSoup(video_page_source, 'lxml')
            # print(video_page_source)
            try:
                # video_url = re.findall('"video_url":"([^"]+)"', video_page_source)[0].replace("\\u0026", "&")
                video_url = self.browser.find_element_by_css_selector("video[type='video/mp4']").get_attribute('src')
                # print(f'Try: {video_url}')
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
                print(f'Except: {video_url}')
            except:
                continue

            try:
                video_title = video_url.split('/')[-1].split('?')[0]
            except AttributeError:
                pass
            else:
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
        my_profile = InstaBot(user_name, user_password, FF_DRIVER)
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
# user_name_box.insert(0, EMAIL_ID)
user_name_box.focus()
user_name_box.grid(column=1, row=2, pady=10)
user_password_box = ttk.Entry(width=30, show='*')
user_password_box.bind("<Button-1>", on_click)
# user_password_box.focus()
user_password_box.grid(column=1, row=3, pady=10)

style = Style()
style.map('TButton', foreground=[('active', '!disabled', 'green')],
          background=[('active', 'black')])
ui_login_button = ttk.Button(text='Login', command=main)
ui_login_button.grid(column=1, row=4)

# Disable window resize option by user
window.resizable(False, False)

window.mainloop()
