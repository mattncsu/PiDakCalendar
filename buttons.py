#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import schedule
import subprocess
import os
from subprocess import call
import notify2
import sys; print(sys.executable)
print(os.getcwd())
#notify2.init("Buttons")

os.environ.setdefault('XAUTHORITY', '/home/user/.Xauthority')
os.environ.setdefault('DISPLAY', ':0.0')
GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #*
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #MIC
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #CAM
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)    #BRIGHTNESS
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)    #POWER


input_state1 = GPIO.input(26)
input_state2 = GPIO.input(19)
input_state3 = GPIO.input(13)
input_state4 = GPIO.input(6)
input_state5 = GPIO.input(5)
print(time.asctime( time.localtime(time.time())))
print('Button State: ', input_state1, input_state2, input_state3, input_state4, input_state5)
rc = subprocess.call(["/home/pi/py_switch/cams.sh", "stop"])
cam_state=False
rc = subprocess.Popen('DISPLAY=:0 notify-send -u critical "Buttons!" "Waiting for you to push something." -i dialog-information', shell=True)
#n = notify2.Notification("Buttons!", "Waiting for you to push something.")
#n.set_urgency(notify2.URGENCY_CRITICAL)
#n.show()
#camstatus = str(subprocess.check_output(["sudo", "screen", "-list"]))
#print(camstatus)
brightness = str(subprocess.check_output(["ddcutil", "getvcp", "10"]))
brightness = brightness[brightness.find('=',4):brightness.find(',')]
brightness = brightness[1:].strip(' ')
if brightness == '0':
    disp_state=1
    print('Startup brightness is 0%')
elif brightness == '1':
    disp_state=0
    print('Display is off')
else:
    disp_state=2
    print('Startup brightness is >0%')  

def job():
    print('Checking for down cameras')
    repaircam = str(subprocess.check_output(["/home/pi/py_switch/cams.sh", "repair"]))
    if not repaircam:
        print("All cameras still running")
    else:
        print(repaircam)

def job1():
    print('Checking for down cameras')
    repaircam = str(subprocess.check_output(["/home/pi/py_switch/cams_inside.sh", "repair"]))
    if not repaircam:
        print("All cameras still running")
    else:
        print(repaircam)
def night():
    rc = subprocess.call(["ddcutil", "setvcp", "10", "1"])
    rc = subprocess.call(["ddcutil", "setvcp", "0xd6", "04"])
    disp_state=0
    print('Starting night mode')

def day():
    rc = subprocess.call(["ddcutil", "setvcp", "0xd6", "01"])
    rc = subprocess.call(["ddcutil", "setvcp", "10", "100"])
    disp_state=2
    print('Starting day mode')

schedule.every().day.at("23:30").do(night)
schedule.every().day.at("06:00").do(day)
schedule.every().wednesday.at("07:15").do(night)
schedule.every().wednesday.at("17:00").do(day)
schedule.every().thursday.at("07:15").do(night)
schedule.every().thursday.at("17:00").do(day)

while True:
    input_state1 = GPIO.input(26)   #*
    input_state2 = GPIO.input(19)   #MIC
    input_state3 = GPIO.input(13)   #CAM
    input_state4 = GPIO.input(6)    #BRIGHTNESS
    input_state5 = GPIO.input(5)    #POWER
    
    if input_state3 == False:
        print('Camera Button Pressed')
        time.sleep(0.2)
        if cam_state == False:
            #n = notify2.Notification("Starting Cameras", "May take up to 10 seconds...", "camera-video")
            rc = subprocess.Popen('DISPLAY=:0 notify-send -u critical "Starting Cameras" "Stay take up to 10 secondsandby..." -i camera-video', shell=True)
            #if not n.show():
             #   print("Failed to send notification")
              #  sys.exit(1)
            rc = subprocess.call(["/home/pi/py_switch/cams.sh", "repair"]) #repair like start but won't double start if running
            cam_state=True
            schedule.every(2).minutes.do(job).tag('repair-cams')
        else:
            #n = notify2.Notification("Stopping Cameras", "Standby...", "camera-video")
            rc = subprocess.Popen('DISPLAY=:0 notify-send -u critical "Stopping Cameras" "Standby..." -i camera-video', shell=True)
            rc = subprocess.call(["/home/pi/py_switch/cams.sh", "stop"])
            cam_state=False
            schedule.clear('repair-cams')
##    if input_state4 == False:
##        print('Brightness button Pressed')
##        rc = subprocess.Popen('DISPLAY=:0 notify-send -u critical "Changing Brightness..." "100% -> 0% -> Off ->" -i dialog-information', shell=True)
##        #n = notify2.Notification("Changing brightness", "100% -> 0% -> Off ->", "dialog-information")
##        time.sleep(0.2)
##        if disp_state == 3:
##               rc = subprocess.call(["ddcutil", "setvcp", "10", "50"])
##               disp_state=2
##        elif disp_state == 2:
##                rc = subprocess.call(["ddcutil", "setvcp", "10", "0"])
##                disp_state=1
##        elif disp_state == 1:
##                rc = subprocess.call(["ddcutil", "setvcp", "10", "1"])
##                rc = subprocess.call(["ddcutil", "setvcp", "0xd6", "04"])
##                disp_state=0
##        elif disp_state == 0:
##                rc = subprocess.call(["ddcutil", "setvcp", "0xd6", "01"])
##                rc = subprocess.call(["ddcutil", "setvcp", "10", "100"])
##                disp_state=2 #changed to 2 to from 3 to bypass 50% brighness
    if input_state5 == False:
        print('Power button Pressed')
        start = time.time()
        time.sleep(0.2)
        rc = subprocess.Popen('DISPLAY=:0 notify-send -u critical "Hold for 5s to shutdown." -i system-shutdown', shell=True)
    #    n = notify2.Notification("Shutdown?", "Hold for 5s to shutdown.", "system-shutdown")
        while input_state5 == False:
            time.sleep(0.1)
            print('Holding down 3')
            end = time.time()
            press_time = end-start
           # print(press_time)
            input_state5 = GPIO.input(5)
            if press_time > 5:
                print('Shutting down?')
                os.system('sudo shutdown -h now')
                
    if input_state2 == False:
        print('Microphone button Pressed')
        time.sleep(0.2)
        #rc = subprocess.call(["ddcutil", "setvcp", "10", "100"])
    if input_state1 == False:
        print('Star button Pressed')
        time.sleep(0.2)
        if cam_state == False:
            #n = notify2.Notification("Starting Cameras", "May take up to 10 seconds...", "camera-video")
            rc = subprocess.Popen('DISPLAY=:0 notify-send -u critical "Starting Cameras" "Stay take up to 10 secondsandby..." -i camera-video', shell=True)
            #if not n.show():
             #   print("Failed to send notification")
              #  sys.exit(1)
            rc = subprocess.call(["/home/pi/py_switch/cams_inside.sh", "repair"]) #repair like start but won't double start if running
            cam_state=True
            schedule.every(2).minutes.do(job1).tag('repair-insidecams')
        else:
            #n = notify2.Notification("Stopping Cameras", "Standby...", "camera-video")
            rc = subprocess.Popen('DISPLAY=:0 notify-send -u critical "Stopping Cameras" "Standby..." -i camera-video', shell=True)
            rc = subprocess.call(["/home/pi/py_switch/cams_inside.sh", "stop"])
            cam_state=False
            schedule.clear('repair-insidecams')
    time.sleep(0.1)
    schedule.run_pending()


