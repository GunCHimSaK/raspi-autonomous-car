# 딥러닝 기반 라즈베리파이 자율주행 버스

라즈베리파이 4B 2대로 만든 소형 자율주행 버스(RC카)의 코드입니다. ELCO 전시회 출품작이고, 2023년에 진행했습니다.
카메라로 차선을 따라 주행하면서 YOLOv5로 신호등과 버스 정류장을 인식하고, 초음파 센서로 앞의 장애물을 감지해 멈춥니다.

## 시스템 구조

```
┌──────────────── Raspberry Pi B (인지) ────────────────┐        ┌──────────── Raspberry Pi A (주행) ────────────┐
│ 카메라 ──▶ YOLOv5 (신호등 / 정류장)               │        │                                                │
│                         │                             │  TCP   │  socket server :12345                          │
│ 초음파 센서 ──▶ 거리 측정 ┼──▶ 주행 판단 ──▶ b'0' / b'1' ─┼──────▶│   b'0' → 전진   b'1' → 정지  ──▶ DC모터 (L298n) │
│ (TRIG 23 / ECHO 24)     │                             │ 유선   │  카메라 ──▶ 차선 인식 ──▶ PID ──▶ 서보 조향     │
└───────────────────────────────────────────────────────┘        └────────────────────────────────────────────────┘
```

딥러닝 객체 인식과 차선 인식을 보드 1대에서 함께 돌리기에는 성능이 부족했습니다. 그래서 보드 2대에 처리를 나누고 이더넷 유선 TCP 소켓으로 연결했습니다.

## 초음파 센서 장애물 감지

인지 보드(B)에서 TRIG/ECHO 방식 초음파 센서로 앞의 장애물까지 거리를 재고, 객체 인식 결과와 합쳐 정지 여부를 판단합니다.

**거리 측정 원리**
1. TRIG 핀에 10µs 펄스를 보내 초음파를 발신합니다.
2. ECHO 핀이 HIGH로 유지되는 시간(왕복 시간)을 잽니다.
3. `거리(cm) = 왕복 시간 × 34300 / 2`

**주행 판단 규칙** (`object_detection/detect.py`의 `send_detection_result`)

| 조건 | 전송 | 동작 |
|---|---|---|
| 장애물 거리 ≤ 15cm | `b'1'` | 정지 (인식 결과와 상관없이 우선 적용) |
| 빨간불 / 노란불 / 정류장 인식 | `b'1'` | 정지 |
| 그 외 (다른 인식 결과, 인식 없음) | `b'0'` | 전진 |

**`sensors/ultrasonic.py`** 는 측정 로직을 따로 떼어낸 모듈입니다.
- 에코 대기에 30ms 타임아웃을 두어, 신호가 돌아오지 않아도 루프에 갇히지 않게 했습니다.
- 5회 측정한 값의 중앙값을 사용해 튀는 값(노이즈)을 걸러냅니다.
- 2~400cm 밖의 값은 버립니다.
- `is_blocked()`로 정지 거리(15cm) 안에 장애물이 있는지 바로 확인할 수 있습니다.

```bash
python3 sensors/ultrasonic.py   # 거리와 STOP/GO 실시간 출력
```

## 폴더 구조

### `object_detection/` — 객체 인식과 초음파 센서 (보드 B)
| 파일 | 설명 |
|---|---|
| `best.pt` | 직접 학습한 YOLOv5 가중치 (신호등, 버스 정류장) |
| `detect.py` | YOLOv5 `detect.py`에 초음파 거리 측정, 주행 판단, 소켓 클라이언트를 통합한 최종 버전 |

```bash
git clone https://github.com/ultralytics/yolov5.git && cd yolov5
pip install -r requirements.txt
# 이 레포의 best.pt와 detect.py를 yolov5 폴더에 복사
python3 detect.py --weights best.pt --conf 0.5 --img 416 --source 0
```
> 보드 A의 IP는 `detect.py`의 `main()`에 있는 `host`에서 설정합니다. `detect.py`는 Ultralytics YOLOv5(AGPL-3.0)를 수정한 파일입니다.

### `sensors/`
| 파일 | 설명 |
|---|---|
| `ultrasonic.py` | 초음파 센서 거리 측정 모듈 (타임아웃, 중앙값 필터) |

### `network/` — 모터 제어 서버 (보드 A)
| 파일 | 설명 |
|---|---|
| `socket_motor_server.py` | TCP 서버(포트 12345). `b'0'`을 받으면 전진, `b'1'`을 받으면 정지 |

### `lane_detection/` — 차선 인식과 주행 (보드 A)
| 파일 | 설명 |
|---|---|
| `aaa.py` | 1차: 좌우 차선 각도를 비교해 `left/right/go/hard left/hard right` 판정 |
| `pcontrol.py` | 2차: PiCamera 영상, 차선 중심 오차에 비례(P) 제어 |
| `adc.py` | 3차: 좌우 차선까지의 거리 차이를 오차로 사용하는 PID 제어(`simple_pid`) |
| `twst281.py` | 4차: 곡선 대응을 위한 슬라이딩 윈도우와 다항식 피팅 차선 추적, PID 제어 |

처리 단계: `Grayscale → Gaussian Blur → Canny → ROI → HoughLinesP → 좌우 차선 분류 → 오차 → P/PID`

### `motor_control/` — DC 모터와 서보
| 파일 | 설명 |
|---|---|
| `dcmo.py` | DC 모터 PWM 전진/후진/정지 테스트 |
| `drive.py` | 전진하면서 서보를 -30°~30°로 왕복 (스레드로 종료 입력 처리) |
| `submo.py` | 각도를 입력받아 서보 조정 |
| `keydcmo.py`, `test.py`, `test2.py`, `pygametest.py` | 키보드(keyboard / pygame)로 수동 조종 |

### `camera/`
| 파일 | 설명 |
|---|---|
| `cameratest.py`, `driving_test810.py` | OpenCV 카메라 화면 확인용 테스트 |

### `setup/`
| 파일 | 설명 |
|---|---|
| `OpenCV-4-5-5.sh` | 라즈베리파이에 OpenCV 4.5.5를 소스 빌드하는 스크립트 |
| `NOTES.md` | 라즈베리파이 초기 설정과 YOLOv5 설치 명령어 정리 |

## 하드웨어

| 구분 | 부품 | GPIO (BCM) |
|---|---|---|
| 연산 | Raspberry Pi 4B 4GB × 2 | |
| 카메라 | Raspberry Pi Camera V1, V2 | |
| 초음파 센서 | TRIG/ECHO 방식 | TRIG 23, ECHO 24 (보드 B) |
| 조향 | MG-996R 서보 | 23 (보드 A, 50Hz) |
| 구동 | GA25-370 DC모터 + L298n | 6, 5 (보드 A) |

## 의존성
```bash
pip install opencv-python numpy RPi.GPIO simple-pid pygame keyboard picamera
```
