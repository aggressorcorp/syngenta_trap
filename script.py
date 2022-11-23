import smtplib
import os
import time
import mimetypes
from pyfiglet import Figlet
from tqdm import tqdm
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
import datetime
import RPi.GPIO as GPIO
import cv2
import matplotlib.pyplot as plt
import numpy as np

def createPhoto():
    date_1 = datetime.datetime.now()
    date = date_1.strftime("%B") + "_" + date_1.strftime("%d")
    hour = date_1.strftime("%H") + "_" + date_1.strftime("%M")
    getPhoto = 'raspistill -o FTP/files/files/Photo_' + '' + date + '_' + hour + '_.jpg -q 100'
    photo_Name = 'Photo_' + '' + date + '_' + hour + '_.jpg'
    photoData = ['1', '2']
    photoData[0] = getPhoto
    photoData[1] = photo_Name
    im = cv2.imread(f'FTP/files/files/{photoname[1]}')
    h, w = img.shape[:2]
    src = np.float32([(886,     501),
			(1945,  514),
			(996,    1635),
			(1796,  1651)])

    dst = np.float32([(1945, 0),
			(0, 0),
			(1945, 1650),
			(0, 1650)])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
	warped = warped[0:1650, 0:1933]
    cv2.imwrite(f'FTP/files/files/{photoname[1]}', warped)
    return photoData


def checkDayStatus():
    test = 0
    i = 1
    while i <= 8:
        if GPIO.input(sensor) > 0:
            test = test + 1
            time.sleep(1)
            i = i + 1
    if test > 5:
        tst = GPIO.input(sensor)
        print(f'That realy Night {tst}')
        return 1
    else:
        tst = GPIO.input(sensor)
        print(f'That not Night {tst}')
        return 0


def getDateforPhoto():
    date_1 = datetime.datetime.now()
    hour_1 = date_1.strftime("%H")
    minute_1 = date_1.strftime("%M")
    detectTime = ['1', '2']
    detectTime[0] = hour_1
    detectTime[1] = minute_1
    return detectTime


def send_email(text=None, template=None):
    sender = "email"
    # your password = "your password"
    password = "pass"
    getsender = "sender"
    #template = "email_template.html"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        with open(template) as file:
            template = file.read()
    except IOError:
        template = None

    try:
        server.login(sender, password)
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = getsender
        msg["Subject"] = "Subject "

        if text:
            msg.attach(MIMEText(text))

        if template:
            msg.attach(MIMEText(template, "html"))

        print("Collecting...")
        for file in tqdm(os.listdir("FTP/files/files")):
            time.sleep(0.4)
            filename = os.path.basename(file)
            ftype, encoding = mimetypes.guess_type(file)
            file_type, subtype = ftype.split("/")

            if file_type == "text":
                with open(f"FTP/files/files/{file}") as f:
                    file = MIMEText(f.read())
            elif file_type == "image":
                with open(f"FTP/files/files/{file}", "rb") as f:
                    file = MIMEImage(f.read(), subtype)
            elif file_type == "audio":
                with open(f"FTP/files/files/{file}", "rb") as f:
                    file = MIMEAudio(f.read(), subtype)
            elif file_type == "application":
                with open(f"FTP/files/files/{file}", "rb") as f:
                    file = MIMEApplication(f.read(), subtype)
            else:
                with open(f"FTP/files/files/{file}", "rb") as f:
                    file = MIMEBase(file_type, subtype)
                    file.set_payload(f.read())
                    encoders.encode_base64(file)

            # with open(f"attachments/{file}", "rb") as f:
            #     file = MIMEBase(file_type, subtype)
            #     file.set_payload(f.read())
            #     encoders.encode_base64(file)

            file.add_header('content-disposition', 'attachment', filename=filename)
            msg.attach(file)

        print("Sending...")
        server.sendmail(sender, getsender, msg.as_string())

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


def main():
    font_text = Figlet(font="slant")
    print(font_text.renderText("SEND EMAIL"))
    text = "Ваше фото:"
    template = ""
    print(send_email(text=text, template=template))


GPIO.setmode(GPIO.BOARD)
sensor = 18
rele = 16

GPIO.setup(rele, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(sensor, GPIO.IN)
GPIO.output(rele, GPIO.OUT)

startmode = True
photoname = createPhoto()
os.system(photoname[0])
time.sleep(5)
if photoname:
    main()
    time.sleep(10)
os.remove(f'FTP/files/files/{photoname[1]}')
while startmode:
    detectTime = getDateforPhoto()
    checkLight = 0
    checkLight = checkDayStatus()
    if checkLight == 1:
        GPIO.output(rele, GPIO.IN)
        time.sleep(5)
    else:
        GPIO.output(rele, GPIO.OUT)
    if detectTime[0] == "7" and detectTime[1] == "10":
        photoname = createPhoto()
        os.system(photoname[0])
        time.sleep(5)
        if photoname:
            main()
            time.sleep(10)
        os.remove(f'FTP/files/files/{photoname[1]}')
    if detectTime[0] == "13" and detectTime[1] == "10":
        photoname = createPhoto()
        os.system(photoname[0])
        time.sleep(5)
        if photoname:
            main()
            time.sleep(10)
        os.remove(f'FTP/files/files/{photoname[1]}')
    if detectTime[0] == "23" and detectTime[1] == "55":
        GPIO.output(rele, GPIO.OUT)
        photoname = createPhoto()
        os.system(photoname[0])
        time.sleep(5)
        if photoname:
            main()
            time.sleep(10)
        os.remove(f'FTP/files/files/{photoname[1]}')
        GPIO.output(rele, GPIO.IN)
