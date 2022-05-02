from fastapi import Request,FastAPI
from fastapi.responses import FileResponse
from uvicorn import run
from PCA9685 import PCA9685
import RPi.GPIO as GPIO
import os.path,sys,time,json,argparse,socket,default
#import default.py from current directoty to get default values

################# Buzzer ################

GPIO.setwarnings(False)
Buzzer_Pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(Buzzer_Pin,GPIO.OUT)
class Buzzer:
    def run(self,command):
        if command!="0":
            GPIO.output(Buzzer_Pin,True)
        else:
            GPIO.output(Buzzer_Pin,False)
    def beep(self,sec):
        count=0
        while count<sec:
            GPIO.output(Buzzer_Pin,True)
            time.sleep(default.WEIGHTBASEUNIT*0.5)
            GPIO.output(Buzzer_Pin,False)
            time.sleep(default.WEIGHTBASEUNIT*0.5)
            count=count+1

    
   
buzzer=Buzzer()

            
############### car control #################
class Motor:
    def __init__(self):
        self.pwm = PCA9685(0x40, debug=True)
        self.pwm.setPWMFreq(50)
    def duty_range(self,duty1,duty2,duty3,duty4):
        if duty1>4095:
            duty1=4095
        elif duty1<-4095:
            duty1=-4095        
        
        if duty2>4095:
            duty2=4095
        elif duty2<-4095:
            duty2=-4095
            
        if duty3>4095:
            duty3=4095
        elif duty3<-4095:
            duty3=-4095
            
        if duty4>4095:
            duty4=4095
        elif duty4<-4095:
            duty4=-4095
        return duty1,duty2,duty3,duty4
        
    def left_Upper_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(0,0)
            self.pwm.setMotorPwm(1,duty)
        elif duty<0:
            self.pwm.setMotorPwm(1,0)
            self.pwm.setMotorPwm(0,abs(duty))
        else:
            self.pwm.setMotorPwm(0,4095)
            self.pwm.setMotorPwm(1,4095)
    def left_Lower_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(3,0)
            self.pwm.setMotorPwm(2,duty)
        elif duty<0:
            self.pwm.setMotorPwm(2,0)
            self.pwm.setMotorPwm(3,abs(duty))
        else:
            self.pwm.setMotorPwm(2,4095)
            self.pwm.setMotorPwm(3,4095)
    def right_Upper_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(6,0)
            self.pwm.setMotorPwm(7,duty)
        elif duty<0:
            self.pwm.setMotorPwm(7,0)
            self.pwm.setMotorPwm(6,abs(duty))
        else:
            self.pwm.setMotorPwm(6,4095)
            self.pwm.setMotorPwm(7,4095)
    def right_Lower_Wheel(self,duty):
        if duty>0:
            self.pwm.setMotorPwm(4,0)
            self.pwm.setMotorPwm(5,duty)
        elif duty<0:
            self.pwm.setMotorPwm(5,0)
            self.pwm.setMotorPwm(4,abs(duty))
        else:
            self.pwm.setMotorPwm(4,4095)
            self.pwm.setMotorPwm(5,4095)
            
 
    def setMotorModel(self,duty1,duty2,duty3,duty4):
        duty1,duty2,duty3,duty4=self.duty_range(duty1,duty2,duty3,duty4)
        self.left_Upper_Wheel(-duty1)
        self.left_Lower_Wheel(-duty2)
        self.right_Upper_Wheel(-duty3)
        self.right_Lower_Wheel(-duty4)
            

#for the loop
#PWM.setMotorModel(2000,2000,2000,2000)       #Forward
#PWM.setMotorModel(-2000,-2000,-2000,-2000)   #Back
#PWM.setMotorModel(-500,-500,2000,2000)       #Left 
#PWM.setMotorModel(2000,2000,-500,-500)       #Right    
#time.sleep(3)
#PWM.setMotorModel(0,0,0,0)                   #Stop
    
################################ DO NOT MODIFY THE CODE ABOVE #################################


""" REST API server, taking instruction from API request """
PWM=Motor()   

# for quick debuging
def dprint(*objects):
    if default.DEBUG:
        print(*objects)

app = FastAPI()

# just for fun and quick testing
@app.get("/",description = "Just the fun and quick test",name="")
@app.get("/chittybang",description = "Just the fun and quick test",name="")
@app.get("/chittychittybangbang",description = "Just the fun and quick test",name="")
def read_root():
    if os.path.exists(default.FPATH):
        return FileResponse(default.FPATH)
    else:
        return ("Happy Racing !!!")

# POSt request handler
@app.post("/chittybang",response_model=default.Wheel,description="Passing the information to the car",name="")
@app.post("/chittychittybangbang",response_model=default.Wheel,description="Passing the information to the car",name="")
async def parse_request(request: Request,wheel: default.Wheel):
    data = await request.body()
    req_data =  json.loads(data)
    dprint("\nJSON from POST request:\n",req_data)
    if "weight" in req_data:        #Translate to how many seconds the car will run before stopping
        weight = req_data["weight"]
        if weight < default.WEIGHTMIN or weight > default.WEIGHTMAX:
            dprint ("\nweight is not in the range, set to default")
            weight = default.WEIGHTMIN # set to default 
    else:
        weight = default.WEIGHTMIN   # set to default
        dprint ("\nweight not found, set to default")
    if "direction" in req_data:     #Move forward or backward
        direction = req_data["direction"]
        if direction not in ["forward","backward"]:
            dprint ("\ndirection is incorrect, set to default")
            direction = default.DIRECTION
    else:
        direction = default.DIRECTION
        dprint ("\ndirection not found, set to default")
    if "speed" in req_data:        #PWM duty cycle, how fast the car runs
        duty = req_data["speed"]
        if duty < default.SPEEDMIN or duty > default.SPEEDMAX:
            dprint ("\nspeed is not in the range, set to default")
            duty = default.SPEED # set to default 
    else:
         duty = default.SPEED
         dprint ("\nspeed not found, set to default")
    dprint ("\nData send to car,weight=%d,direction=%s,speed=%d\n"%(weight,direction,duty))
    
    if direction == "forward":        
        PWM.setMotorModel(duty,duty,duty,duty)       #Send car forward
        time.sleep(weight*default.WEIGHTBASEUNIT)
        PWM.setMotorModel(0,0,0,0)                   #Stop car
       
    if direction == "backward":
        PWM.setMotorModel(-duty,-duty,-duty,-duty)   #Send car backward
        buzzer.beep(weight)
        #time.sleep(weight*default.WEIGHTBASEUNIT)
        PWM.setMotorModel(0,0,0,0)                   #Stop car

    return (req_data) # echo request data

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255",1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

def main():
    hostip = get_ip()
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',dest='server_ip',type=str,default=hostip,help='REST server IP address, default=current IP')
    parser.add_argument('-p',dest='port',type=int,default=8888,help='port number in request url, default=8888')
    parser.add_argument('-d',dest='debug',type=bool,default=False,help='debug flag, default=False')
    parser.add_argument('-u',dest='unit',type=float,default=0.5,help='weight base unit, default=0.5')
    args = parser.parse_args()
    
    host = args.server_ip
    port = args.port
    default.DEBUG=args.debug
    default.WEIGHTBASEUNIT=args.unit
    
    #Start server
    try:
        run("car:app",host=host,port=port)
    except:
        print ("Something went wrong, cannot setup server, maybe check network, host IP or port number?")

if __name__ == '__main__':
    sys.exit(main())
    
