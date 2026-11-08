# 라즈베리파이 설정 메모 (SD카드의 bash 기록에서 정리)

## 기본 설정과 한글 입력
```bash
sudo apt update && sudo apt full-upgrade
sudo apt install ibus ibus-hangul fonts-nanum fonts-unfonts-core
sudo reboot
```

## YOLOv5 설치
```bash
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip install -r requirements.txt
sudo apt install libopenblas-dev libblas-dev m4 cmake cython python3-dev python3-yaml python3-setuptools
python3 detect.py --source 0 --weights yolov5s.pt --conf 0.25   # 기본 모델 테스트
python3 detect.py --weights best.pt --conf 0.5 --img 416 --source 0   # 신호등 모델
```

## 카메라 (레거시 카메라 스택)
```bash
sudo raspi-config        # Interface Options → Camera 활성화
sudo apt-get install python3-picamera
raspistill -o test.jpg   # 촬영 테스트
```

## VS Code
```bash
sudo apt install code
```

## Wi-Fi 설정
```bash
sudo iwlist wlan0 scan
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
