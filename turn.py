
import threading
import time
from onvif import ONVIFCamera
from zeep import Client
import cv2 as cv
import numpy as np
import time

XMAX = 1                        
XMIN = -1
YMAX = 1
YMIN = -1

def perform_move(ptz, request, timeout):
    ptz.ContinuousMove(request)                         # Начать непрерывное движение
    time.sleep(timeout)                                 # Подождать
    ptz.Stop(request)                                   # Остановить

def move_up(ptz, request, timeout=2):
    print('move up...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMAX
    perform_move(ptz, request, timeout)

def move_down(ptz, request, timeout=2):
    print('move down...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMIN
    perform_move(ptz, request, timeout)

def move_right(ptz, request, timeout=2):
    print('move right...')
    if request.Velocity is None:
        request.Velocity = ptz.create_type('PTZSpeed')
    if request.Velocity.PanTilt is None:
        request.Velocity.PanTilt = ptz.create_type('PanTilt')
    global XMAX, XMIN, YMAX, YMIN
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = 0
    perform_move(ptz, request, timeout)

def move_left(ptz, request, timeout=2):
    print('move left...')
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = 0
    perform_move(ptz, request, timeout)

class Video_Capture:
    def __init__(self, name):
        self.cap = cv.VideoCapture(name)                    # захват видео с указанного источника
        self.lock = threading.Lock()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    def _reader(self):                                      # захват снимка сразу после его появления
        while True:
            with self.lock:
                ret = self.cap.grab()
            if not ret:
                break

    def read(self):                                         # извлечение последнего кадра
        with self.lock:
            _, frame = self.cap.retrieve()                  # извлекаем последний захваченный кадр
        return frame

def continuous_move():
    mycam = ONVIFCamera('192.168.1.108', 80, 'admin', 'admin123', 'C:\\Users\\Valery\\Desktop\\Project\\python-onvif-zeep\\wsdl')
    media = mycam.create_media_service()                            # Создать объект медиа-сервиса
    ptz = mycam.create_ptz_service()                                # Создать объект сервиса ptz
    media_profile = media.GetProfiles()[0]                          # Получить целевой профиль
    
    cap = Video_Capture('rtsp://admin:admin123@192.168.1.108')

    default_pan = 0.10583333333333345                               # стандартные значения положения камеры
    default_tilt = 0.6659047619047618
    default_zoom = 0.6466666666666666

    print(f"Стандартное положение камеры: Pan: {default_pan}, Tilt: {default_tilt}, Zoom: {default_zoom}")

    angles = [0, 90, 180, 270] 
    snapshots = []
    
    moverequest = ptz.create_type('AbsoluteMove')
    moverequest.ProfileToken = media_profile.token
    moverequest.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    
    Start = time.time()
    
    reverse = False
    delta_x = 0.06
    for i in range (8):
        if reverse == True:
            default_pan -= delta_x 
        else: default_pan += delta_x

        if i == 3:
            reverse = True
            
        end = time.time()
        print("Время выполнения кода:", end-Start, "секунд(ы)")

        moverequest.Position.PanTilt.x = default_pan
        moverequest.Position.PanTilt.y = default_tilt
        
        ptz.AbsoluteMove(moverequest)                           # Выполняем движение камеры

        cv.waitKey(300)
        
        frame = cap.read()                                      # Захват кадра и сохранение
        print(f'{cap} считал')
        # filename = f"camera_snapshot_{angle}.jpg"
        # cv.imwrite(filename, frame)                           # Сохраняем кадр
        snapshots.append(frame)                                 # Добавляем кадр в список
    
    end = time.time()
    print("Общее Время выполнения кода:", end-Start, "секунд(ы)")
    
    collage = create_collage(snapshots, angles + angles[::-1])  # Создаем панораму из всех снимков
    cv.imshow("Collage", collage)
    cv.waitKey(0)
    cv.destroyAllWindows()

def create_collage(snapshots, angles):
                                                                                        # Вычисляем размеры для коллажа
    width = 640                                                                         # Ширина каждого снимка
    height = 480                                                                        # Высота каждого снимка
    collage_height = height * 2                                                         # Высота коллажа для двух рядов
    collage = np.zeros((collage_height, width * len(snapshots), 3), dtype=np.uint8)     # Создаем пустое изображение для коллажа

    for i, snapshot in enumerate(snapshots):
        resized_snapshot = cv.resize(snapshot, (width, height))                     # Изменяем размер снимка
        if i < 4:
            collage[0:height, i * width:(i + 1) * width] = resized_snapshot         # Вставляем снимок в верхний ряд
        else:
            collage[height:collage_height, (i - 4) * width:((i - 4) + 1) * width] = resized_snapshot  # Вставляем снимок в нижний ряд
        cv.putText(collage, f"{angles[i]}°", (i * width + 10, 30 if i < 4 else height + 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # Добавляем угол поворота

    return collage

if __name__ == '__main__':
    continuous_move()
