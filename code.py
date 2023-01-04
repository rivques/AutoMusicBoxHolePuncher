import time # pyright: reportShadowedImports=false
from lib.utils import *
import asyncio
from adafruit_motor.stepper import StepperMotor
from adafruit_motor.servo import Servo
import sys
from pwmio import PWMOut
import board
import adafruit_logging

class HolePuncher:
    logger = adafruit_logging.getLogger()
    motor_logger = adafruit_logging.Logger("motor", 10) # level 10 is debug level
    
    _hole_puncher_state = HolePuncherState.OFF

    # # hardware
    # x_stepper_pins = [
    #     PWMOut(board.D2),
    #     PWMOut(board.D3),
    #     PWMOut(board.D4),
    #     PWMOut(board.D5)
    # ]
    # x_stepper = StepperController(StepperMotor(*x_stepper_pins))
    # y_stepper_pins = [
    #     PWMOut(board.D6),
    #     PWMOut(board.D7),
    #     PWMOut(board.D8),
    #     PWMOut(board.D9)
    # ]
    # y_stepper = StepperController(StepperMotor(*y_stepper_pins))
    # z_servo_a = Servo(PWMOut(board.D10, duty_cycle=2 ** 15, frequency=50), min_pulse=500, max_pulse=2500)
    # z_servo_b = Servo(PWMOut(board.D11, duty_cycle=2 ** 15, frequency=50), min_pulse=500, max_pulse=2500)
    # drill_motor = PWMOut(board.D12)

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
        self.hole_puncher_state = HolePuncherState.STARTUP
        self.logger.setLevel(10)

    async def run_ui(self):
        # ui loop, will call itself again if it's still turned on
        
        if(self.hole_puncher_state != HolePuncherState.OFF):
            asyncio.run(self.run_ui)

    def parse_file(file):
        # parse a txt file of a song and return a list of Operations
        pass
    
    def punch_holes(operations):
        self.hole_puncher_state = HolePuncherState.PUNCHING
        # given a list of Operations, execute them
        for operation in operations:
            # again, rust match would be so nice here
            if operation.operationType == OperationType.PROGRAMSTART:
                pass
async def async_test():
    while True:
        print("Hello async!")
        await asyncio.sleep(1)

async def input_test():
    theInput = await ainput("aInput!")
    print(theInput)
asyncio.create_task(async_test())
asyncio.run(input_test())
if False and __name__ == "__main__":
    holePuncher = HolePuncher()
    asyncio.run(holePuncher.run_ui())
    asyncio.get_event_loop().run_forever()