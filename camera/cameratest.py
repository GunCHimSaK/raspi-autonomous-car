import cv2

def main():
    #0은 기본 카메라를 의미합니다. 여러대의 카메라가 연결되어 있을 경우 1, 2 등으로 바꿔주면 됩니다.
    cap = cv2.VideoCapture(0)

    # 카메라가 제대로 연결되었는지 확인
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        exit()

    while True:
        # 카메라로부터 프레임을 읽어옴
        ret, frame = cap.read()

        # 프레임 읽기에 실패하면 종료
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        # 화면에 프레임을 출력
        cv2.imshow('Camera Feed', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 종료 전에 모든 자원을 해제
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
