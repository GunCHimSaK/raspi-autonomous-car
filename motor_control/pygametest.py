import pygame
import RPi.GPIO as GPIO
import time

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

# DC 모터 제어 함수
def move_forward():
    GPIO.output(motor1_pin1, GPIO.HIGH)
    GPIO.output(motor1_pin2, GPIO.LOW)

def move_backward():
    GPIO.output(motor1_pin1, GPIO.LOW)
    GPIO.output(motor1_pin2, GPIO.HIGH)

def stop_motor():
    GPIO.output(motor1_pin1, GPIO.LOW)
    GPIO.output(motor1_pin2, GPIO.LOW)

# 서보모터 제어 함수
def control_servo(duty):
    pwm = GPIO.PWM(servo_pin, 50)  # PWM 주파수 설정
    pwm.start(0)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # 움직임을 안정화하기 위한 지연 시간
    pwm.stop()

# pygame 초기화
pygame.init()

# 화면 생성 (사용하지 않으므로 크기 1x1)
screen = pygame.display.set_mode((1, 1))

# 키 상태 변수 초기화
up_pressed = False
down_pressed = False
left_pressed = False
right_pressed = False

# 초기 서보모터 duty 설정
servo_duty = 7.5
control_servo(servo_duty)

# 이벤트 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:  # 위 방향키를 누를 때
                move_forward()
                up_pressed = True
            elif event.key == pygame.K_DOWN:  # 아래 방향키를 누를 때
                move_backward()
                down_pressed = True
            elif event.key == pygame.K_LEFT:  # 왼쪽 방향키를 누를 때
                left_pressed = True
            elif event.key == pygame.K_RIGHT:  # 오른쪽 방향키를 누를 때
                right_pressed = True
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:  # 위 방향키를 떼었을 때
                up_pressed = False
            elif event.key == pygame.K_DOWN:  # 아래 방향키를 떼었을 때
                down_pressed = False
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT: 
                right_pressed = False
                left_pressed = False

        elif event.type == pygame.QUIT:
            running = False
    
    output = ""
    if up_pressed:
        output += "DC up "
    elif down_pressed:
        output += "DC down"
    else:
        stop_motor()
    
    if left_pressed:
        output += "L"
        control_servo(5.83)
    elif right_pressed:
        output += "R"
        control_servo(9.17)
    else:
        control_servo(7.5)
    
    print(output)

# DC 모터 정지
stop_motor()

# GPIO 해제
GPIO.cleanup()

# pygame 종료
pygame.quit()
