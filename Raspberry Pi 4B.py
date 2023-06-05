import spidev
import time
import RPi.GPIO as GPIO

# 피에조부저 핀 번호 지정
piezoLeft = 20
piezoRight = 16

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(piezoLeft, GPIO.OUT)
GPIO.setup(piezoRight, GPIO.OUT)

spi = spidev.Spidev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def readChannel(channel):
    val = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((val[1] & 3) << 8) + val[2]
    return data

# 채널에서 데이터 값을 받아오고 이를 사용한 센서(GP2YOA21)에 맞는 거리변환 공식 사용
def distance(channel):
    vol = readChannel(channel) / 1023.0 * 3.3
    distance = (16.2537 * vol**4 - 129.893 * vol**3 + 382.268 * vol**2 - 512.611 * vol + 301.439) / 2
    return distance

# 거리에 따라 피에조 부저 작동 빈도수 조절 (거리 값이 더 낮을 수록 더 자주)
def delay(distance):
    delaytime = distance / 100
    time.sleep(delaytime)

if __name__ == "__main__":
    try:
        pwmLeft = GPIO.PWM(piezoLeft, 262)
        pwmRight = GPIO.PWM(piezoRight, 262)

        while True:
            distL = distance(0)
            distM = distance(1)
            distR = distance(2)

            # 60cm 안에 물체가 인식 된 경우

            # 가운데(또는 왼쪽과 오른쪽 센서 동시에) 물체가 인식되었을 때
            if (distL <= 60 and distR <= 60) or distM <= 60:
                pwmLeft.start(10.0)
                time.sleep(0.25)
                pwmLeft.stop()
                pwmRight.start(10.0)
                time.sleep(0.25)
                pwmRight.stop()
                delay(min(distL, distM, distR))
            
            # 왼쪽 센서에만 물체가 인식되었을 때
            elif distL <= 60:
                pwmLeft.start(10.0)
                time.sleep(0.5)
                pwmLeft.stop()
                delay(distL)

            # 오른쪽 센서에만 물체가 인식되었을 때
            elif distR <= 60:
                pwmRight.start(10.0)
                time.sleep(0.5)
                pwmRight.stop()
                delay(distR)

            else:
                time.sleep(0.5)

    # 종료
    except KeyboardInterrupt:
        pwmLeft.stop()
        pwmRight.stop()
        GPIO.cleanup()
        pass
