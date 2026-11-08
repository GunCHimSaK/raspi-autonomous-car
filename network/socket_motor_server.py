import RPi.GPIO as GPIO
import time
import socket

# GPIO 핀 번호 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 사용할 핀 번호
in1_pin = 6
in2_pin = 5

# GPIO 핀 설정
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)

# PWM 설정 (주파수는 100Hz)
pwm1 = GPIO.PWM(in1_pin, 50)
pwm2 = GPIO.PWM(in2_pin, 50)

# 모터 속도 (0~100 사이)
pwm_speed = 30

# PWM 시작 (초기 듀티 사이클은 0)
pwm1.start(0)
pwm2.start(0)

# 앞으로 회전 함수
def forward():
    pwm1.ChangeDutyCycle(pwm_speed)  # in1_pin에 pwm_speed 적용
    pwm2.ChangeDutyCycle(0)  # in2_pin은 0 (LOW)

# 모터 정지 함수
def stop():
    pwm1.ChangeDutyCycle(0)  # in1_pin을 0 (LOW)로 설정
    pwm2.ChangeDutyCycle(0)  # in2_pin을 0 (LOW)로 설정

# 서버 설정
SERVER_IP = ''
SERVER_PORT = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)
print("Waiting for connection...")
client_socket, addr = server_socket.accept()
print(f"Connected to {addr}")

# 클라이언트로부터 데이터 수신
try:
    while True:
        data = client_socket.recv(1)
        if data == b'1':
            stop()
            print("Motor stopped.")
        elif data == b'0':
            forward()
            print("Motor running forward.")
        else:
            print(f"Unknown command: {data}")

except KeyboardInterrupt:
    stop()

finally:
    # PWM 정지
    pwm1.stop()
    pwm2.stop()
    client_socket.close()
    server_socket.close()
    GPIO.cleanup()
