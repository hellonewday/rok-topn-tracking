#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from ppadb.client import Client
from PIL import Image
import numpy as np
import io
import cv2
from time import sleep
import easyocr
import pandas as pd
import datetime

reader = easyocr.Reader(['vi','en'])

## hypeparameters

## NUMBER OF GOVERNORS
NUMBER_OF_GOVERNORS = 300
KINGDOM = 2719
# Ordinary
X = 0
Y = 0
W = 850
H = 360
# ID
ID_X = 415
ID_Y = 60
ID_W = 150
ID_H = 38
# Name
NAME_X = 305
NAME_Y = 90
NAME_W = 310
NAME_H = 40
# POWER - Apply blur
POWER_X = 500
POWER_Y = 170
POWER_W = 160
POWER_H = 40

# KILL POINTS
KILL_X = 30
KILL_Y = 150
KILL_W = 330
KILL_H = 200

# PREKVK
PRE_X = 800
PRE_Y = 250
PRE_W = 250
PRE_H = 100

shrink_width = 850
shrink_height = 350

shrink_mini_width = 550
shrink_mini_height = 350

shrink_large_width = 1200
shrink_large_height = 800

adb = Client(host='127.0.0.1',port=5037)
devices = adb.devices()

def connect_device():
    adb = Client(host='127.0.0.1',port=5037)
    devices = adb.devices()
    if len(devices) == 0:
        print("No Devices Attached")
        quit()
    return devices[0]

def converImagePilToCV(ImagePIL):
    open_cv_image = np.array(ImagePIL) 
    open_cv_image = cv2.cvtColor(open_cv_image,cv2.COLOR_RGB2BGR)
    return open_cv_image

def convertScreenToImage(screen):
    byteImage = Image.open(io.BytesIO(screen))
    image = converImagePilToCV(byteImage)
    return image

def scrollDown():
    device.input_swipe(950,550,950,140, 1000)
    print("I'm scrolling down")
    sleep(1)
    

def extractInfomation_v2(img,shrink_w, shrink_h, x, y, w, h, apply_blur=False):
    def preprocess_overall_profile_v2(sw, sh, profile):
        gray_img = cv2.cvtColor(profile, cv2.COLOR_BGR2GRAY)
        thresh_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_OTSU)[1]

        cnts = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        global new_profile
        for c in cnts:
                x,y,w,h = cv2.boundingRect(c)
                if(w >= profile.shape[0] / 2 and h >= profile.shape[1] / 4):
#                     cv2.rectangle(profile, (x, y), (x + w, y + h), (36,255,12), 3)
                    new_profile = profile[y:y+h,x:x+w]
                    new_profile = cv2.resize(new_profile,(sw,sh))
        return new_profile
    preprocess_img = preprocess_overall_profile_v2(shrink_w, shrink_h, img)
#     cv2.rectangle(preprocess_img, (x, y), (x + w, y + h), (36,255,12), 3)
    id_image = preprocess_img[y:y+h,x:x+w]
    if apply_blur == True:
        id_image = cv2.blur(id_image,(3,3))
    id_image = cv2.cvtColor(id_image, cv2.COLOR_BGR2GRAY)
    id_image = cv2.threshold(id_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU )[1]
    return id_image

## Specific for power - id - name with matrix input
def production_api_v2(profileImage):
    powerImage = extractInfomation_v2(profileImage,shrink_width,shrink_height,POWER_X,POWER_Y,POWER_W,POWER_H,False)
    power = reader.readtext(powerImage)[0][1]
    
    idImage = extractInfomation_v2(profileImage,shrink_width,shrink_height,ID_X,ID_Y,ID_W,ID_H,False)
    ID = reader.readtext(idImage)[0][1]
    
    nameImage = extractInfomation_v2(profileImage,shrink_width,shrink_height,NAME_X,NAME_Y,NAME_W,NAME_H,False)
    name = reader.readtext(nameImage)[0][1]
    
    return ID, name, power

## Specific for kill point with matrix input
def production_api_v3(killImage):
    x = 860
    y = 580
    w = 150
    h = 240
    # cv2.rectangle(kill_point_image, (x,y), (x + w, y + h), (255,0,0), 3)
    personal_box = killImage[y:y+h,x:x+w]
    gray_img = cv2.cvtColor(personal_box, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    killpoints = reader.readtext(thresh_img)
    points = []
    for killpoint in killpoints:
        points.append(killpoint[1])

    return points

## Even more specific with personal info with matrix input
def production_api_v4(infoImage):
    x = 1000
    y = 250
    w = 330
    h = 600


    # cv2.rectangle(spec_image, (x,y), (x + w, y + h), (255,0,0), 3)
    personal_box = infoImage[y:y+h,x:x+w]
    gray_img = cv2.cvtColor(personal_box, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    killpoints = reader.readtext(thresh_img)
    specificInfo = []
    for killpoint in killpoints:
        specificInfo.append(killpoint[1])
        
    return specificInfo

#write to csv file
device = connect_device()
print("Connect to device ", device.get_serial_no())
init_x = 300
init_y = 300
init_w = 30
init_h = 30
# image = images[0]
# cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 3)
# cv2.imshow("image",image)
# cv2.waitKey(0)
# images = []
datasets = []
for i in range(0,NUMBER_OF_GOVERNORS):
    if(i <= 3):
        x = init_x
        y = init_y + (100*i)
        w = init_w
        h = init_h
    else:
        x = 300
        y = 600
        w = 30
        h = 30
    print("Click on coords: ", (x,y,w,h))
##### START FROM HERE - LOOP BEGIN
    device.input_tap(x + w, y + h)
    print("Starting getting player ", i + 1)
    sleep(2)
    
    screen = device.screencap()
    image1 = convertScreenToImage(screen)
    id, name, power = production_api_v2(image1)
    print("Finish capturing general info of player ", i + 1)
    
    x = 1100
    y = 350
    w = 30
    h = 30
    device.input_tap(x + w, y + h)
    sleep(3)
    screen = device.screencap()
    image2 = convertScreenToImage(screen)
    killpoints = production_api_v3(image2)
    print("Finish capturing kill point info of player ", i + 1)
    
    x = 400
    y = 600
    w = 30
    h = 30
    device.input_tap(x + w, y + h)
    sleep(2)
    screen = device.screencap()
    image3 = convertScreenToImage(screen)
    specificInfo = production_api_v4(image3)
    print("Finish capturing specific info of player", i+1)
#     images.append([image1,image2,image3])

    x = 1400
    y = 30
    w = 30
    h = 30
    device.input_tap(x + w, y + h)
    print("Exiting specific info of player ", i+1)
    sleep(2)

    x = 1350
    y = 100
    w = 30
    h = 30
    device.input_tap(x + w, y + h)
    print("Finish capturing player ", i + 1)
    sleep(2)
    
    if(len(specificInfo) == 7):
        datasets.append({
            'ID': id.replace(")",""),
            'Governor Name': name,
            'Power': power.replace(",","."),
            'Kill T1': killpoints[0].replace(",","."),
            'Kill T2': killpoints[1].replace(",","."),
            'Kill T3': killpoints[2].replace(",","."),
            'Kill T4': killpoints[3].replace(",","."),
            'Kill T5': killpoints[4].replace(",","."),
            'Max Power': specificInfo[0].replace(",","."),
            "Victories": specificInfo[1].replace(",","."),
            "Loses": specificInfo[2].replace(",","."),
            "Dead": specificInfo[3].replace(",","."),
            "Scouts": specificInfo[4].replace(",","."),
            "Resources": specificInfo[5].replace(",","."),
            "Resources Sent": 0,
            "Alliance Help": specificInfo[6].replace(",",".")
        })
    else:
        datasets.append({
            'ID': id.replace(")",""),
            'Governor Name': name,
            'Power': power.replace(",","."),
            'Kill T1': killpoints[0].replace(",","."),
            'Kill T2': killpoints[1].replace(",","."),
            'Kill T3': killpoints[2].replace(",","."),
            'Kill T4': killpoints[3].replace(",","."),
            'Kill T5': killpoints[4].replace(",","."),
            'Max Power': specificInfo[0].replace(",","."),
            "Victories": specificInfo[1].replace(",","."),
            "Loses": specificInfo[2].replace(",","."),
            "Dead": specificInfo[3].replace(",","."),
            "Scouts": specificInfo[4].replace(",","."),
            "Resources": specificInfo[5].replace(",","."),
            "Resources Sent": specificInfo[6].replace(",","."),
            "Alliance Help": specificInfo[7].replace(",",".")
        })


df = pd.json_normalize(datasets)
df.to_excel("Daily Report Kingdom 2719.xlsx",index=False,verbose=True)
df

