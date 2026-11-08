import RPi.GPIO as GPIO
import time
import pygame

# DC 모터 핀 설정
motor1_pin1 = 5
motor1_pin2 = 6

# 서보모터 핀 설정
servo_pin = 23

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(motor1_pin1, GPIO.OUT)
GPIO.setup(motor1_pin2, GPIO.OUT)
GPIO.setup(servo_pin, GPIO.OUT)

# 서보모터 제어 함수
def control_servo(angle):
    pwm = GPIO.PWM(servo_pin, 50)  # PWM 주파수 설정
    pwm.start(0)
    pulse = (angle / 180) * 2000 + 500
    duty = pulse / 200
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # 움직임을 안정화하기 위한 지연 시간
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)
    pwm.stop()

# 전진 함수
def move_forward():
    GPIO.output(motor1_pin1, GPIO.HIGH)
    GPIO.output(motor1_pin2, GPIO.LOW)

# 후진 함수
def move_backward():
    GPIO.output(motor1_pin1, GPIO.LOW)
    GPIO.output(motor1_pin2, GPIO.HIGH)

# 초기 설정
control_servo(90)

# pygame 초기화
pygame.init()

# 키보드 입력 감지
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:  # 'w' 키 입력 시 전진
                move_forward()
            elif event.key == pygame.K_s:  # 's' 키 입력 시 후진
                move_backward()
            elif event.key == pygame.K_a:  # 'a' 키 입력 시 서보모터를 120도로 회전
                control_servo(25)
            elif event.key == pygame.K_d:  # 'd' 키 입력 시 서보모터를 60도로 회전
                control_servo(-25)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_s:  # 'w' 또는 's' 키를 떼었을 때 모터 정지
                GPIO.output(motor1_pin1, GPIO.LOW)
                GPIO.output(motor1_pin2, GPIO.LOW)
            elif event.key == pygame.K_a or event.key == pygame.K_d:  # 'a' 또는 'd' 키를 떼었을 때 서보모터 초기 위치로 복귀
                control_servo(0)
