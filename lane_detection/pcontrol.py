import cv2
import numpy as np
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO


# 모터 드라이버 핀 설정
IN1 = 20
IN2 = 21
IN3 = 23
IN4 = 24

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# 모터 핀을 PWM 모드로 설정
pwm_left = GPIO.PWM(IN1, 100)  # 첫 번째 인자는 핀 번호, 두 번째 인자는 주파수(Hz)
pwm_right = GPIO.PWM(IN3, 100)

# PWM 시작 (초기 듀티 사이클은 0)
pwm_left.start(0)
pwm_right.start(0)

def set_motor_speed(speed_left, speed_right):
    # 속도 값이 음수인 경우, 모터의 회전 방향을 바꿉니다.
    if speed_left < 0:
        GPIO.output(IN2, GPIO.HIGH)
        speed_left = -speed_left
    else:
        GPIO.output(IN2, GPIO.LOW)

    if speed_right < 0:
        GPIO.output(IN4, GPIO.HIGH)
        speed_right = -speed_right
    else:
        GPIO.output(IN4, GPIO.LOW)

    # 듀티 사이클 설정 (0 ~ 100 사이의 값)
    speed_left = min(100, max(0, speed_left))
    speed_right = min(100, max(0, speed_right))

    pwm_left.ChangeDutyCycle(speed_left)
    pwm_right.ChangeDutyCycle(speed_right)


def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blurred, 300, 300)
    
    height, width = canny.shape
    vertices = np.array([[(0, height), (width // 2, height // 2), (width, height)]], dtype=np.int32)
    cropped_image = region_of_interest(canny, vertices)

    lines = cv2.HoughLinesP(cropped_image, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=5)
    return lines

def draw_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return line_image

def control_steering(image, lines):
    if lines is None or len(lines) == 0:
        return

    # 왼쪽 차선 및 오른쪽 차선의 점을 저장할 리스트
    left_points = []
    right_points = []

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        slope = (y2 - y1) / (x2 - x1)
        if slope < 0:
            left_points.append((x1, y1))
            left_points.append((x2, y2))
        else:
            right_points.append((x1, y1))
            right_points.append((x2, y2))

    height, width, _ = image.shape
    center_x = width // 2
    center_y = int(height * (4/5))  # 화면 하단 1/3 위치로 y 좌표 설정
    cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)  # 빨간색 원으로 표시
    
    left_lane_x = np.mean([point[0] for point in left_points if point[1] == center_y])
    right_lane_x = np.mean([point[0] for point in right_points if point[1] == center_y])
    left_distance = center_x - left_lane_x if not np.isnan(left_lane_x) else None
    right_distance = right_lane_x - center_x if not np.isnan(right_lane_x) else None

    # 거리 출력
    print(f"ld: {left_distance}")
    print(f"rd: {right_distance}")

    # 차선 거리 계산 및 스티어링 제어


    distance_diff = 0  # distance_diff 변수 초기화

    if not np.isnan(left_lane_x) and not np.isnan(right_lane_x):
        distance_diff = (center_x - left_lane_x) - (right_lane_x - center_x)

    # PID 제어를 사용하여 속도 조절 (여기서는 간단한 비례 제어만 구현합니다)
    Kp = 1  # 비례 상수, 실험을 통해 적절한 값을 찾으십시오.
    speed_diff = Kp * distance_diff

    base_speed = 30  # 기본 속도, 실험을 통해 적절한 값을 찾으십시오.
    speed_left = base_speed - speed_diff
    speed_right = base_speed + speed_diff

    set_motor_speed(speed_left, speed_right)

# 카메라 설정
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
raw_capture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)

try:
    for frame in camera.capture_continuous(raw_capture, format='bgr', use_video_port=True):
        image = frame.array
        raw_capture.truncate(0)

        lines = process_image(image)
        line_image = draw_lines(image, lines)
        combined_image = cv2.addWeighted(image, 0.8, line_image, 1, 0)

        control_steering(image, lines)

        cv2.imshow('frame', combined_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
             break

except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()

# 프로그램 종료
cv2.destroyAllWindows()
