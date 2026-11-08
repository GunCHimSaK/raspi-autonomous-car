# 라즈베리파이 자율주행 RC카 프로젝트

라즈베리파이로 RC카를 만들면서 작성한 코드 모음입니다. (2023년 3월 ~ 11월, 이후 CAN 통신 테스트 추가)
라즈베리파이를 판매하기 전에 SD카드를 백업해 두었고, 그 백업과 PC에 있던 코드를 정리해서 올렸습니다.

주요 내용:
- **차선 인식**: OpenCV(Canny 엣지 검출과 Hough 변환)로 차선을 찾고, P/PID 제어로 좌우 모터 속도를 조절
- **모터 제어**: L298N 계열 드라이버로 DC 모터를 제어하고, PWM으로 서보 조향
- **신호등 인식**: YOLOv5로 직접 학습한 신호등 검출 모델(`best.pt`)
- **원격 제어**: 키보드(pygame/keyboard)와 TCP 소켓으로 모터 제어
- **CAN 통신**: 라즈베리파이에서 STM32로 스로틀과 조향 값 전송

---

## 폴더 구조

### `lane_detection/` — 차선 인식과 주행
| 파일 | 설명 |
|---|---|
| `aaa.py` | 차선 기울기 검출. ROI 사다리꼴 마스크, HoughLinesP로 좌우 차선 각도를 구해 `left/right/go/hard left/hard right` 출력 |
| `adc.py` | 차선까지의 좌우 거리 차이를 오차로 사용하는 **PID 제어**(`simple_pid`) 기반 차동 구동 (GPIO 20/21/23/24) |
| `pcontrol.py` | PiCamera 영상으로 차선을 검출하고 **비례(P) 제어**로 좌우 모터 속도 조절 |
| `twst281.py` | 슬라이딩 윈도우와 다항식 피팅(`find_lane_pixels`, `fit_polynomial`)으로 차선을 추적하고 PID 제어 |

### `motor_control/` — DC 모터와 서보
| 파일 | 설명 |
|---|---|
| `dcmo.py` | DC 모터 PWM 전진/후진/정지 테스트 (GPIO 6, 5) |
| `drive.py` | DC 모터로 전진하면서 서보를 -30°~30°로 왕복. `q` 입력 시 종료(스레드 사용) |
| `submo.py` | 각도를 입력받아 서보 각도를 조정 (GPIO 23, 50Hz) |
| `keydcmo.py` | 방향키(↑/↓)로 DC 모터 제어 (`keyboard` 라이브러리) |
| `test.py` | W/S 키로 전후진, A/D/E 키로 조향 |
| `test2.py` | pygame 키 이벤트로 W/A/S/D 주행 |
| `pygametest.py` | pygame 방향키로 주행과 조향 (최종 수동 조종 버전) |

### `network/`
| 파일 | 설명 |
|---|---|
| `socket_motor_server.py` | TCP 서버(포트 12345). `0`을 받으면 전진, `1`을 받으면 정지. 신호등 인식 PC와 연동하는 용도 *(원래 파일명: `untitled.py`)* |

### `camera/`
| 파일 | 설명 |
|---|---|
| `cameratest.py`, `driving_test810.py` | OpenCV 카메라 화면 확인용 테스트 |

### `can_bus/`
| 파일 | 설명 |
|---|---|
| `can.py` | `python-can`(socketcan, `can0`)으로 ID `0x100`에 스로틀과 조향 값(×1000, big-endian short 2개)을 0.5초 간격으로 전송. STM32 수신 테스트용 |

### `traffic_light_yolov5/` — 신호등 인식
| 파일 | 설명 |
|---|---|
| `best.pt` | 직접 학습한 YOLOv5 신호등 검출 가중치 (약 14MB) |
| `detect.py` | 라즈베리파이에서 돌아가도록 수정한 YOLOv5 `detect.py` (warmup 크기 처리 수정, `ultralytics` 패키지의 Annotator 사용) |

실행 방법:
```bash
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip install -r requirements.txt
# 이 레포의 best.pt와 detect.py를 yolov5 폴더에 복사한 뒤
python3 detect.py --weights best.pt --conf 0.5 --img 416 --source 0
```
> `detect.py`는 Ultralytics YOLOv5(AGPL-3.0)를 수정한 파일입니다.

### `setup/`
| 파일 | 설명 |
|---|---|
| `OpenCV-4-5-5.sh` | 라즈베리파이 32비트 OS에 OpenCV 4.5.5를 소스 빌드하는 스크립트 (약 2시간 소요) |
| `NOTES.md` | 라즈베리파이 초기 설정 과정에서 썼던 명령어 정리 |

---

## 하드웨어 / 핀 배치 (코드 기준)
| 용도 | GPIO (BCM) |
|---|---|
| DC 모터 (단일 모터 + 서보 조향 버전) | IN1=6, IN2=5 (일부 코드는 5/6 반대로 사용) |
| 서보 조향 | 23 (50Hz) |
| 좌우 차동 구동 버전 | IN1=20, IN2=21, IN3=23, IN4=24 |
| CAN | `can0` (MCP2515 등 SPI-CAN 모듈) |

## 의존성
```bash
pip install opencv-python numpy RPi.GPIO simple-pid pygame keyboard picamera python-can
```

## 레포에 포함하지 않은 것
용량이 커서 원본 백업에만 남겨 둔 파일입니다.
- 신호등 검출 결과 영상 `runs/detect/exp*/0.mp4` (최대 260MB)
- `yolov5-trafficlight.zip`(540MB), `yolov5-lightstation.zip`(940MB)
- 테스트 사진(`tes814_*.jpg` 등)과 스크린샷
- 원본 YOLOv5 코드 전체 (업스트림 레포에서 받으면 됨)
