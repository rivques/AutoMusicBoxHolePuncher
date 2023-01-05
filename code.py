from lib.utils import * # pyright: reportShadowedImports=false
import asyncio
from adafruit_motor.stepper import StepperMotor
from adafruit_motor.servo import Servo
import sys
from pwmio import PWMOut
import board
import adafruit_logging
import digitalio

class HolePuncher:
    logger = adafruit_logging.getLogger()
    motor_logger = adafruit_logging.Logger("motor", 10) # level 10 is debug level
    
    _hole_puncher_state = HolePuncherState.OFF

    # hardware
    raw_stepper = StepperMotor(PWMOut(board.D2, frequency=2000), PWMOut(board.D3, frequency=2000), PWMOut(board.D4, frequency=2000), PWMOut(board.D5, frequency=2000))
    x_stepper = StepperController(raw_stepper)
    y_stepper = StepperController(StepperMotor(PWMOut(board.D6, frequency=2000), PWMOut(board.D7, frequency=2000), PWMOut(board.D8, frequency=2000), PWMOut(board.D9, frequency=2000)))
    z_servo_a = Servo(PWMOut(board.SDA, duty_cycle=2 ** 15, frequency=50), min_pulse=500, max_pulse=2500)
    z_servo_b = Servo(PWMOut(board.A5, duty_cycle=2 ** 15, frequency=50), min_pulse=500, max_pulse=2500)
    drill_motor = PWMOut(board.D11)

    @property
    def hole_puncher_state(self):
        return self._hole_puncher_state
    
    @hole_puncher_state.setter
    def hole_puncher_state(self, newValue):
        # here's the on state change code
        if newValue == HolePuncherState.OFF:
            asyncio.get_event_loop().stop()
        elif newValue == HolePuncherState.STARTUP:
            pass
        elif newValue == HolePuncherState.IDLE:
            pass
        elif newValue == HolePuncherState.PUNCHING:
            pass
        else:
            raise ValueError(f"Unknown state value! Must be one of {', '.join([key for key in HolePuncherState.keys])}")
        self._hole_puncher_state = newValue

    def __init__(self) -> None:
        self.logger.setLevel(10)
        self.hole_puncher_state = HolePuncherState.STARTUP
        

    async def run_ui(self):
        # ui loop, will call itself again if it's still turned on
        if self.hole_puncher_state == HolePuncherState.OFF:
            return
        elif self.hole_puncher_state == HolePuncherState.STARTUP:
            pass
        elif self.hole_puncher_state == HolePuncherState.IDLE:
            pass
        elif self.hole_puncher_state == HolePuncherState.PUNCHING:
            pass
        
    def parse_file(self, file):
        # parse a txt file of a song and return a list of Operations
        pass
    
    async def punch_holes(self, operations):
        self.hole_puncher_state = HolePuncherState.PUNCHING
        # given a list of Operations, execute them
        for operation in operations:
            # again, rust match would be so nice here
            if operation.operationType == OperationType.PROGRAMSTART:
                pass
            elif operation.operationType == OperationType.PROGRAMEND:
                self.hole_puncher_state = HolePuncherState.IDLE
                return
            elif operation.operationType == OperationType.PUNCHNOTE:
                pass
            elif operation.operationType == OperationType.ADVANCEPAPER:
                pass

if __name__ == "__main__":
    holePuncher = HolePuncher()
    asyncio.run(holePuncher.run_ui())
    asyncio.get_event_loop().run_forever()