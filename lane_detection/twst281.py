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

def find_lane_pixels(binary_warped):
    histogram = np.sum(binary_warped[binary_warped.shape[0] // 2:, :], axis=0)
    midpoint = np.int(histogram.shape[0] // 2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    nwindows = 9
    margin = 100
    minpix = 50

    window_height = np.int(binary_warped.shape[0] // nwindows)

    nonzero = binary_warped.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])

    leftx_current = leftx_base
    rightx_current = rightx_base

    left_lane_inds = []
    right_lane_inds = []

    for window in range(nwindows):
        win_y_low = binary_warped.shape[0] - (window + 1) * window_height
        win_y_high = binary_warped.shape[0] - window * window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin

        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                          (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                           (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)

        if len(good_left_inds) > minpix:
            leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)

    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    return leftx, lefty, rightx, righty

def fit_polynomial(binary_warped):
    leftx, lefty, rightx, righty = find_lane_pixels(binary_warped)

    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    ploty = np.linspace(0, binary_warped.shape[0] - 1, binary_warped.shape[0])
    left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
    right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]

    return left_fitx, right_fitx, ploty

def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 300, 300)

    mask = np.zeros_like(edges)
    height, width = frame.shape[:2]
    bottom_half = height // 2
    left_bottom = (width // 4, height)
    right_bottom = (width * 4 // 5, height)
    left_top = (width // 5, bottom_half)
    right_top = (width * 4 // 5, bottom_half)

    vertices = np.array([[left_bottom, left_top, right_top, right_bottom]], dtype=np.int32)

    
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(edges, mask)

    left_fitx, right_fitx, ploty = fit_polynomial(masked)

    out_img = np.dstack((masked, masked, masked))

    for idx in range(len(ploty)):
        cv2.circle(out_img, (int(left_fitx[idx]), int(ploty[idx])), 3, (255, 0, 0), -1)
        cv2.circle(out_img, (int(right_fitx[idx]), int(ploty[idx])), 3, (0, 0, 255), -1)

    result = cv2.addWeighted(image, 1, out_img, 0.6, 0)

    return result, left_fitx, right_fitx, ploty

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
        result, left_fitx, right_fitx, ploty = process_image(frame)
        cv2.imshow('ImageWindow', result)

        error = left_fitx[-1] - right_fitx[-1]
        control_value = pid_controller(error)

        base_speed = 100
        left_speed = base_speed - control_value
        right_speed = base_speed + control_value
        left_speed = np.clip(left_speed, 0, 100)
        right_speed = np.clip(right_speed, 0, 100)
        set_motor_speed(left_speed, right_speed)

        if abs(left_fitx[-1] - right_fitx[-1]) > 50:
            if left_fitx[-1] > right_fitx[-1]:
                print('left')
            else:
                print('right')
        else:
            print('go')

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

# 종료 시 GPIO 정리
GPIO.cleanup()
cv2.destroyAllWindows()


