from datetime import datetime, timedelta
# from msilib.schema import Media
from time import sleep
from onvif import ONVIFCamera
from zeep import Client
import cv2 as cv
                                                        # Границы для движения
XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1

def perform_move(ptz, request, timeout):
    ptz.ContinuousMove(request)                         # Начать непрерывное движение
    sleep(timeout)                                      # Подождать
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

def continuous_move():
    mycam = ONVIFCamera('192.168.1.108', 80, 'admin', 'admin123', 'C:\\Users\\Valery\\Desktop\\Project\\python-onvif-zeep\\wsdl')
    media = mycam.create_media_service()                            # Создать объект медиа-сервиса
    ptz = mycam.create_ptz_service()                                # Создать объект сервиса ptz
    
        # Получение медиа-сервиса
    #media = mycam.create_media_service()

    """media_profile = media.GetProfiles()[0]  # Получаем профиль

    try:
        options = media.GetVideoEncoderConfigurationOptions({'ProfileToken': media_profile.token}) # Получение параметров кодирования видео
        #print("Параметры конфигурации видеокодера:")                                  # вывод 
        #print(options)
    except Exception as e:
        print(f'Ошибка при получении параметров кодирования видео: {e}')

    configurations_list = media.GetVideoEncoderConfigurations()         # Получение списка конфигураций кодирования видео
    video_encoder_configuration = configurations_list[0]

    video_encoder_configuration.Quality = options.QualityRange.Min      # Установка параметров кодирования видео
    video_encoder_configuration.Encoding = 'H264'  # H264H, H265
    video_encoder_configuration.RateControl.FrameRateLimit = 25
    video_encoder_configuration.Resolution = {
        'Width': 1280,  # 1920
        'Height': 720   # 1080
    }

    video_encoder_configuration.Multicast = {
        'Address': {
            'Type': 'IPv4',
            'IPv4Address': '224.1.0.1',
            'IPv6Address': None
        },
        'Port': 40008,
        'TTL': 64,
        'AutoStart': False,
        '_value_1': None,
        '_attr_1': None
    }

    video_encoder_configuration.SessionTimeout = timedelta(seconds=60)

    request = media.create_type('SetVideoEncoderConfiguration')
    request.Configuration = video_encoder_configuration
    request.ForcePersistence = True
    media.SetVideoEncoderConfiguration(request)"""
    
    """                                                         Получение информации об устройстве
    device_info = mycam.devicemgmt.GetDeviceInformation()           
    print("Manufacturer:", device_info.Manufacturer)
    print("Model:", device_info.Model)
    print("Firmware Version:", device_info.FirmwareVersion)
    print("Serial Number:", device_info.SerialNumber)
    print("Hardware ID:", device_info.HardwareId)
    """
    
    media_profile = media.GetProfiles()[0]                          # Получить целевой профиль
    #print(media_profile)

    # wsdl_url = 'http://192.168.1.108/onvif/device_service?wsdl'     # URL камеры
    # client = None                                                   # Инициализируем переменную client
    
    moverequest = ptz.create_type('AbsoluteMove')
    moverequest.ProfileToken = media_profile.token
    moverequest.Position=ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    
    try: 
        moverequest.Position.PanTilt.x = 0.0    # 0.0 параллельно потолку min шаг +0.05. 1.0 - max положение
        moverequest.Position.PanTilt.y = 0.0    # параллельно потолку вниз -0.05 1.0 - max положение
        moverequest.Position.Zoom.x = 0.0       # min zoom min шаг +0.05 1.0 - max положение
    except:
        pass
    
    def get_snapshots():
        cap = cv.VideoCapture(f'192.168.1.108', 80, 'admin', 'admin123', 'C:\\Users\\Valery\\Desktop\\Project\\python-onvif-zeep\\wsdl')
            
        ret, frame = cap.read()
        if ret:
            # Генерация уникального имени для снимка на основе времени
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f'Image/snapshot_{timestamp}.jpg'
            # Сохранение снимка
            cv.imwrite(filename, frame)
            print(f'Скриншот сохранен как {filename}.')
        else:
            print('Не удалось получить снимок.')
        cap.release()

    ptz.AbsoluteMove(moverequest)
    
if __name__ == '__main__':
    continuous_move()