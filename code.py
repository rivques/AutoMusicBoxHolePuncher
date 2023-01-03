import time # pyright: reportShadowedImports=false
from utils import *
import asyncio
from adafruit_motor.stepper import StepperMotor
import sys

class HolePuncher:
    
    _hole_puncher_state = HolePuncherState.OFF

    # hardware
    x_stepper = StepperMotor()

    @property
    def hole_puncher_state(self):
        return self._hole_puncher_state
    
    @hole_puncher_state.setter
    def hole_puncher_state(self, newValue):
        # here's the on state change code
        if newValue == HolePuncherState.OFF:
            pass
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

    async def run_ui(self):
        # ui loop, will call itself again if it's still turned on
        
        if(self.hole_puncher_state != HolePuncherState.OFF):
            asyncio.run(self.run_ui)

    def parse_file(file):
        # parse a txt file of a song and return a list of Operations
        pass
    
    def punch_holes(operations):
        # given a list of Operations, execute them
        pass

if __name__ == "__main__":
    holePuncher = HolePuncher()
    asyncio.run(holePuncher.run_ui())