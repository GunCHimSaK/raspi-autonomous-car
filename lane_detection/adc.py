import cv2
import numpy as np
import RPi.GPIO as GPIO
from time import sleep
from simple_pid import PID

# GPIO 설정
IN1 = 20
IN2 = 21
IN3 = 23
IN4 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# PWM 설정
freq = 100
left_pwm = GPIO.PWM(IN1, freq)
right_pwm = GPIO.PWM(IN3, freq)
left_pwm.start(0)
right_pwm.start(0)

def set_motor_speed(left_speed, right_speed):
    if left_speed > 0:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)

    if right_speed > 0:
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    else:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)

    left_pwm.ChangeDutyCycle(abs(left_speed))
    right_pwm.ChangeDutyCycle(abs(right_speed))

def process_image(src):
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 100, 200)
    return edges

def set_ROI(src):
    height, width = src.shape
    mask = np.zeros_like(src)
    roi_vertices = np.array([[(0, int(3*height/5)), (width//2, int(3*height/5)), (width, int(3*height/5)), (width, height), (0, height)]])
    cv2.fillPoly(mask, roi_vertices, 255)
    roi = cv2.bitwise_and(src, mask)
    return roi

def find_lines_and_distances(src):
    lines = cv2.HoughLinesP(src, 1, np.pi/180, 50, minLineLength=30, maxLineGap=50)
    center_x = src.shape[1] // 2
    center_y = int(4 * src.shape[0] / 5)
    left_lane_distance = None
    right_lane_distance = None
    left_lane = None
    right_lane = None

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1)
            if np.abs(slope) < 0.5:
                continue
            if slope < 0:
                if left_lane is None or x1 < left_lane[0]:
                    left_lane = line[0]
            else:
                if right_lane is None or x1 > right_lane[0]:
                    right_lane = line[0]

        if left_lane is not None:
            left_x_intercept = left_lane[0] + (center_y - left_lane[1]) / ((left_lane[3] - left_lane[1]) / (left_lane[2] - left_lane[0]))
            left_lane_distance = np.sqrt((center_x - left_x_intercept)**2 + (center_y - center_y)**2)

        if right_lane is not None:
            right_x_intercept = right_lane[0] + (center_y - right_lane[1]) / ((right_lane[3] - right_lane[1]) / (right_lane[2] - right_lane[0]))
            right_lane_distance = np.sqrt((center_x - right_x_intercept)**2 + (center_y - center_y)**2)

    return left_lane, right_lane, left_lane_distance, right_lane_distance

def draw_lines(src, left_lane, right_lane, left_lane_distance, right_lane_distance):
    center_x = src.shape[1] // 2
    center_y = int(4 * src.shape[0] / 5)

    if left_lane is not None and left_lane_distance is not None:
        cv2.line(src, (left_lane[0], left_lane[1]), (left_lane[2], left_lane[3]), (255, 0, 0), 5)
        cv2.circle(src, (int(center_x - left_lane_distance), center_y), 5, (0, 255, 0), -1)

    if right_lane is not None and right_lane_distance is not None:
        cv2.line(src, (right_lane[0], right_lane[1]), (right_lane[2], right_lane[3]), (255, 0, 0), 5)
        cv2.circle(src, (int(center_x + right_lane_distance), center_y), 5, (0, 255, 0), -1)

    cv2.circle(src, (center_x, center_y), 5, (0, 0, 255), -1)
    return src

# PID 컨트롤러 생성 및 설정
kp = 1.0
ki = 0.0
kd = 0.0
pid_controller = PID(kp, ki, kd, setpoint=0)

# 주요 코드 실행 부분
cap = cv2.VideoCapture(0)
while cap.isOpened():

    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (640, 360))
        edges = process_image(frame)
        roi = set_ROI(edges)
        left_lane, right_lane, left_lane_distance, right_lane_distance = find_lines_and_distances(roi)

        if left_lane_distance and right_lane_distance:
            error = left_lane_distance - right_lane_distance
            control_value = pid_controller(error)

            base_speed = 100
            left_speed = base_speed - control_value
            right_speed = base_speed + control_value
            left_speed = np.clip(left_speed, 0, 100)
            right_speed = np.clip(right_speed, 0, 100)
            set_motor_speed(left_speed, right_speed)
            print("Left Speed:", left_speed, "Right Speed:", right_speed)
            

        result = draw_lines(frame, left_lane, right_lane, left_lane_distance, right_lane_distance)
        cv2.imshow('ImageWindow', result)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

# 종료 시 GPIO 정리
GPIO.cleanup()
cap.release()
cv2.destroyAllWindows()

