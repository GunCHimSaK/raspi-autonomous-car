import time
import statistics
import RPi.GPIO as GPIO

TRIG = 23
ECHO = 24
SOUND_SPEED = 34300
STOP_DISTANCE = 15
TIMEOUT = 0.03


class Ultrasonic:
    def __init__(self, trig=TRIG, echo=ECHO, samples=5):
        self.trig = trig
        self.echo = echo
        self.samples = samples
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trig, False)
        time.sleep(0.2)

    def _measure_once(self):
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        start = time.time()
        deadline = start + TIMEOUT
        while GPIO.input(self.echo) == 0:
            start = time.time()
            if start > deadline:
                return None

        end = time.time()
        deadline = end + TIMEOUT
        while GPIO.input(self.echo) == 1:
            end = time.time()
            if end > deadline:
                return None

        return (end - start) * SOUND_SPEED / 2

    def distance(self):
        values = []
        for _ in range(self.samples):
            d = self._measure_once()
            if d is not None and 2 <= d <= 400:
                values.append(d)
            time.sleep(0.01)
        if not values:
            return None
        return statistics.median(values)

    def is_blocked(self, limit=STOP_DISTANCE):
        d = self.distance()
        return d is not None and d <= limit

    def cleanup(self):
        GPIO.cleanup((self.trig, self.echo))


if __name__ == "__main__":
    sensor = Ultrasonic()
    try:
        while True:
            d = sensor.distance()
            if d is None:
                print("out of range")
            else:
                print(f"{d:.1f} cm {'STOP' if d <= STOP_DISTANCE else 'GO'}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        sensor.cleanup()
