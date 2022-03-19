import os
import re
import tkinter.messagebox

import requests
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Style
from PIL import Image, ImageTk
from bs4 import BeautifulSoup


def main():
    download_dir = os.path.expanduser('~').replace('\\', '/') + '/Downloads'
    url = url_box.get()
    if url == '':
        tkinter.messagebox.showwarning(title='Empty URL', message='There is no URL provided to download')
        return
    elif 'https://www.instagram.com/reel' not in url and 'https://www.instagram.com/p' not in url:
        tkinter.messagebox.showerror(title='Invalid URL', message='The URL you provided is incorrect')
        return
    video_data = requests.get(url)
    video_page_source = video_data.text
    soup = BeautifulSoup(video_page_source, 'lxml')
    try:
        video_url = re.findall('"video_url":"([^"]+)"', video_page_source)[0].replace("\\u0026", "&")
    except IndexError:
        video_url = None
        for data in (str(soup.prettify()).split('\n')):
            if '.mp4?efg=' in data:
                temp = data.split(',')
                for element in temp:
                    if '.mp4?efg=' in element:
                        video_url = element.replace('"url":', '').strip('"').replace('\\u0026', '&')
                        break
    video_title = video_url.split('/')[-1].split('?')[0]
    os.chdir(download_dir)
    r = requests.get(video_url)
    with open(video_title, 'wb') as video_file:
        video_file.write(r.content)

    if os.path.exists(f'{download_dir}/{video_title}'):
        tkinter.messagebox.showinfo(title="Done", message="Download Completed Successfully")
    else:
        tkinter.messagebox.showwarning(title='Failed', message='Download Failed')


def on_click(event):
    event.widget.delete(0, END)


def return_key(event):
    main()


window = Tk()
window.title("Instagram Downloader")
window.geometry("500x300")
window.configure(background='white', highlightthickness=True)
window.iconbitmap('images/insta-downloader-icon.ico')

canvas = Canvas(width=400, height=200, background='white', highlightthickness=False)
image = (Image.open('images/insta_logo.png'))
resized_image = image.resize((200, 100), Image.ANTIALIAS)
logo = ImageTk.PhotoImage(resized_image)
canvas.create_image(100, 0, image=logo, anchor="nw")
canvas.grid(column=1, row=0)

window.bind('<Return>', return_key)

url_box = ttk.Entry(width=50)
url_box.bind("<Button-1>", on_click)
url_box.grid(column=1, row=2)

url_text = canvas.create_text(190, 190, text="Paste URL Here", fill="blue", font=("Courier", 13, "italic"))
canvas.grid(column=1, row=1)

style = Style()
style.map('TButton', foreground=[('active', '!disabled', 'green')],
          background=[('active', 'black')])
download_button = ttk.Button(text='Download', command=main)
download_button.grid(column=2, row=2)

# Disable window resize option by user
window.resizable(False, False)

window.mainloop()