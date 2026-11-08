import RPi.GPIO as GPIO
import time
import threading

# 서보 모터 설정
def set_angle(a):
    angle = 90 + a
    pulse = (angle / 180) * 2000 + 500
    duty = pulse / 200
    return duty

servo_pin = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)
pwm_servo = GPIO.PWM(servo_pin, 50)
pwm_servo.start(0)

# DC 모터 설정
in1_pin = 6
in2_pin = 5
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)
pwm1 = GPIO.PWM(in1_pin, 50)
pwm2 = GPIO.PWM(in2_pin, 50)
pwm_speed = 30
pwm1.start(0)
pwm2.start(0)

# 앞으로 회전
def forward():
    pwm1.ChangeDutyCycle(pwm_speed)
    pwm2.ChangeDutyCycle(0)

# 모터 정지
def stop():
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)

# 왕복 주행
def drive():
    forward()
    while not exit_signal:
        for a in range(-30, 31, 1):
            if exit_signal:
                break
            duty = set_angle(a)
            pwm_servo.ChangeDutyCycle(duty)
            time.sleep(0.05)

        for a in range(30, -31, -1):
            if exit_signal:
                break
            duty = set_angle(a)
            pwm_servo.ChangeDutyCycle(duty)
            time.sleep(0.05)
        
    stop()

# 종료 함수
def quit_program():
    global exit_signal
    while not exit_signal:
        user_input = input("종료하려면 'q'를 입력하세요: ")
        if user_input.lower() == 'q':
            exit_signal = True

exit_signal = False

if __name__ == "__main__":
    drive_thread = threading.Thread(target=drive)
    quit_thread = threading.Thread(target=quit_program)

    drive_thread.start()
    quit_thread.start()

    drive_thread.join()
    quit_thread.join()

    # PWM 정지
    pwm_servo.stop()
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
