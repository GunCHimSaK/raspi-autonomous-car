import cv2

# 카메라 객체 생성
cap = cv2.VideoCapture(0)  # 0은 기본 카메라를 의미합니다.

# 카메라가 정상적으로 열렸는지 확인
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 무한 루프로 카메라 영상 표시
while True:
    ret, frame = cap.read()  # 카메라에서 프레임 읽기

    if not ret:
        print("카메라에서 프레임을 읽을 수 없습니다.")
        break

    # 프레임 표시
    cv2.imshow("카메라 영상", frame)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료 시 카메라와 창 해제
cap.release()
cv2.destroyAllWindows()

