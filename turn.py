
import threading
import time
from onvif import ONVIFCamera
from zeep import Client
import cv2 as cv
                                                        
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

    positions = [
        (0.3, 0.0),   # Угол 0°
        (0.5, 0.0),   # Угол 90°
        (0.7, 0.0),   # Угол 180°
        (0.9, 0.0)    # Угол 270°
    ]
    
    angles = [0, 90, 180, 270]
    snapshots = []

    for pos, angle in zip(positions, angles):                  # Устанавливаем позицию камеры
        moverequest = ptz.create_type('AbsoluteMove')
        moverequest.ProfileToken = media_profile.token
        moverequest.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position

        moverequest.Position.PanTilt.x = pos[0]
        moverequest.Position.PanTilt.y = pos[1]
        
        ptz.AbsoluteMove(moverequest)                           # Выполняем движение камеры

        cv.waitKey(500)                                         #  Время поворота
        
        #time.sleep(1)

        frame = cap.read()                                      # Захват кадра и сохранение
        print(f'{cap} считал')
        filename = f"camera_snapshot_{angle}.jpg"
        cv.imwrite(filename, frame)                             # Сохраняем кадр
        snapshots.append(frame)                                 # Добавляем кадр в список

    for i, snapshot in enumerate(snapshots):
        cv.imshow(f'Snapshot {angles[i]}°', snapshot)

    cv.waitKey(0)
    cv.destroyAllWindows()

    moverequest.Position.PanTilt.x = 0.0                        # Возвращаем камеру в исходное положение           
    moverequest.Position.PanTilt.y = 0.0
    moverequest.Position.Zoom.x = 0.0
    ptz.AbsoluteMove(moverequest)
    
if __name__ == '__main__':
    
    continuous_move()