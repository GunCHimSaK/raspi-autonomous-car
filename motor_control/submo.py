import RPi.GPIO as GPIO
import time

def set_angle(a):
    angle = 90 + a
    pulse = (angle / 180) * 2000 + 500
    duty = pulse / 200
    return duty

def main():
    servo_pin = 23  # 서보 모터가 연결된 GPIO 핀 번호 (핀 번호는 환경에 따라 변경될 수 있음)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)

    pwm = GPIO.PWM(servo_pin, 50) # 50Hz
    pwm.start(0)

    try:
        while True:
            a = float(input("각도 조정을 위한 a 값을 입력하세요 (-90 to 90): "))
            duty = set_angle(a)
            pwm.ChangeDutyCycle(duty)
            time.sleep(1) # 1초 동안 각도 유지

    except KeyboardInterrupt:
        print("종료합니다.")
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
