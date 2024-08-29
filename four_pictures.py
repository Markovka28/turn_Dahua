import numpy as np
import cv2 as cv
import logging
import time
import requests

logging.basicConfig(level=logging.INFO)             #Установка уровня логирования

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1
DEFAULT_TIMEOUT = 2                                    #интервал на 2 секунды

PTZ_URL = 'http://192.168.1.108/onvif/ptz_serice'

cap = cv.VideoCapture('rtsp://admin:admin123@192.168.1.108')
if not cap.isOpened():
    logging.error("Не удается открыть камеру")
    exit()
    
def get_xml(direction):
    velocity_x = 0
    velocity_y = 0
    if direction == "left":
        velocity_x = -0.5
    elif direction == "right":
        velocity_x = 0.5
    elif direction == "up":
        velocity_y = -0.5
    elif direction == "down":
        velocity_y = 0.5
    
    xml = f'''<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Header>
    <Security s:mustUnderstand="1" xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <UsernameToken><Username>admin</Username>
    <Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">
    VqXfUmP6Og5+7E4KVFf3Y4gg7Lk=</Password>
    <Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">
    ElpgXl/LE06qtXYQUpOvYX4AAAAAAA==</Nonce><Created xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
    2024-08-22T05:33:48.160Z</Created> </UsernameToken></Security></s:Header><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"><ContinuousMove xmlns="http://www.onvif.org/ver20/ptz/wsdl">
    <ProfileToken>MediaProfile00000</ProfileToken><Velocity><PanTilt x="{velocity_x}" y="{velocity_y}" 
    xmlns="http://www.onvif.org/ver10/schema"/></Velocity></ContinuousMove></s:Body></s:Envelope>'''
    
    return xml

def move_camera(direction):                             #Функция для управления движением камеры
    #try:
        headers = {'Content-Type': 'application/soap+xml; charset=utf-8; action="http://www.onvif.org/ver10/device/wsdl/GetSystemDateAndTime'}
        logging.info("Направление: %s", direction)  
        
        xml = get_xml(direction)
        logging.info("xml: %s", xml)  
        
        response = requests.post(f"{PTZ_URL}", data=xml, headers=headers)
        time.sleep(0.5)
        
        xml = get_xml('stop')
        response = requests.post(f"{PTZ_URL}", data=xml, headers=headers) 
        
        logging.info("запрос произведен")
        logging.info("response: %s", response)
        
        ''' 
        if response.status_code == 200:
            logging.info(f"Камера переместилась {direction}")
        else:
            logging.error(f"Не удалось переместить камеру: {response.status_code}")
    except Exception as e:
        logging.error(f"Ошибка при перемещении камеры: {e}")
        '''
        
current_direction = None
while True:
    ret, frame = cap.read()                             # Фиксируй кадр за кадром
                                                        #если кадр считан правильно, значение ret равно True

    if not ret:
        logging.error("Не удается получить кадр (stream end?). Вернуть ...")
        continue

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)        # Операции с каркасом 
    cv.imshow('frame', gray)                            # Отображение полученного кадра

    key = cv.waitKey(1)

    if key == ord('q'):
        break                                               # Выход из цикла при нажатии 'q'
    elif key == ord('w'):                                   # Вверх
        logging.info("Кнопка 'W' нажата: движение вверх")

        current_direction = 'up'
    elif key == ord('s'):
        logging.info("Кнопка 'S' нажата: движение вниз")    # Вниз

        current_direction = 'down'
    elif key == ord('a'): 
        logging.info("Кнопка 'A' нажата: движение влево")   # Влево

        current_direction = 'left'
    elif key == ord('d'):
        logging.info("Кнопка 'D' нажата: движение вправо")  # Вправо

        current_direction = 'right'
    elif key == 13:                                     # Enter
        if current_direction:
            for i in range(4):                          # Делаем 4 снимка
                move_camera(current_direction)
                time.sleep(0.5)                         # Пауза 0.5 секунды между снимками
            time.sleep(DEFAULT_TIMEOUT - 2)             # Пауза 2 секунды после серии снимков
        else:
            logging.info("Направление не установлено. Нажмите 'w', 's', 'a' или 'd' для установки направления.")





















