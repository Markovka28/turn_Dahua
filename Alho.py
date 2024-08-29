from pyptz.onvif_control import ONVIFCamera

onvif_camera = ONVIFCamera('192.168.1.108', 80, 'admin', 'admin123')
pan, tilt, zoom = onvif_camera.get_ptz_status()
ptz_service = onvif_camera.create_ptz_service()
ptz_status = ptz_service.GetStatus()
print(pan, tilt, zoom)

