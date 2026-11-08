import RPi.GPIO as GPIO
import keyboard

# GPIO 초기화 및 경고 비활성화
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# DC 모터 핀 설정
motor_pin1 = 6
motor_pin2 = 5

# GPIO 핀 설정
GPIO.setup(motor_pin1, GPIO.OUT)
GPIO.setup(motor_pin2, GPIO.OUT)

# 모터 제어 함수
def control_motor(direction):
    if direction == 'up':
        GPIO.output(motor_pin1, GPIO.HIGH)
        GPIO.output(motor_pin2, GPIO.LOW)
    elif direction == 'down':
        GPIO.output(motor_pin1, GPIO.LOW)
        GPIO.output(motor_pin2, GPIO.HIGH)
    elif direction == 'stop':
        GPIO.output(motor_pin1, GPIO.LOW)
        GPIO.output(motor_pin2, GPIO.LOW)

# 키보드 입력 감지 및 모터 제어
while True:
    if keyboard.is_pressed('up'):
        control_motor('up')
    elif keyboard.is_pressed('down'):
        control_motor('down')
    else:
        control_motor('stop')
