import RPi.GPIO as GPIO
import keyboard
import time

servo_pin = 23

# GPIO 초기화 및 경고 비활성화
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


GPIO.setup(servo_pin, GPIO.OUT)

# DC 모터 핀 설정
motor_pin1 = 5
motor_pin2 = 6

# GPIO 핀 설정
GPIO.setup(motor_pin1, GPIO.OUT)
GPIO.setup(motor_pin2, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)  # PWM 주파수: 50Hz
pwm.start(0)

def control_angle(a):
    angle = 90 + a
    pulse = ( angle / 180 ) * 2000 + 500
    duty = ( pulse / 200 )
    
    pwm.ChangeDutyCycle(duty)
    print(duty)
    #time.sleep(1)
    
# 모터 제어 함수
def control_motor(direction):
    if direction == 'w':
        GPIO.output(motor_pin1, GPIO.HIGH)
        GPIO.output(motor_pin2, GPIO.LOW)
    elif direction == 's':
        GPIO.output(motor_pin1, GPIO.LOW)
        GPIO.output(motor_pin2, GPIO.HIGH)
    elif direction == 'stop':
        GPIO.output(motor_pin1, GPIO.LOW)
        GPIO.output(motor_pin2, GPIO.LOW)

# 키보드 입력 감지 및 모터 제어
while True:
    if keyboard.is_pressed('w'):
        control_motor('w')
    elif keyboard.is_pressed('s'):
        control_motor('s')
    elif keyboard.is_pressed('a'):
        control_angle(-25)
    elif keyboard.is_pressed('d'):
        control_angle(20)
    elif keyboard.is_pressed('e'):
        control_angle(0) 
    else:
        control_motor('stop')

try:
    set_angle_zero()   # 0도로 설정하고 정지
    time.sleep(1)

except KeyboardInterrupt:
    # Ctrl+C 입력 시 예외 처리 및 정지
    pwm.stop()

finally:
    GPIO.cleanup()  # GPIO 설정 초기화
