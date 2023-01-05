import time
import adafruit_motor.stepper as stepper
import asyncio
import adafruit_logging
import sys
import supervisor

def enum(*enum_keys): # https://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    enums = {enum_key: enum_key for enum_key in enum_keys}
    enums["keys"] = enums.keys()
    return type('Enum', (), enums)

async def ainput(string: str) -> str:
    sys.stdout.write(string)
    theInput = ""
    while "\n" not in theInput:
        await asyncio.sleep(0)
        #test for thing on line
        if(supervisor.runtime.serial_bytes_available):
            theNewInput = sys.stdin.read(1)
            sys.stdout.write(theNewInput)
            theInput += theNewInput
    return theInput
            

HolePuncherState = enum("OFF", "STARTUP", "IDLE", "PUNCHING")

OperationType = enum("PROGRAMSTART", "PROGRAMEND", "PUNCHNOTE", "ADVANCEPAPER")

class Operation: # i really wish I could use Rust enums for this, they're perfect for the usecase
    def __init__(self, operationType, operationValue):
        self.operationType = operationType
        self.operationValue = operationValue
        self.logger = adafruit_logging.getLogger("motor")

class StepperController:
    def __init__(self, in_stepper, mm_per_degree = .1, degrees_per_tick = 1.8, lower_step_limit = 0, upper_step_limit = 1000): # TODO: Improve this with actual numbers
        self.stepper: stepper.StepperMotor = in_stepper
        self.ticks: float = 0
        self.degrees_per_tick = degrees_per_tick
        self.mm_per_degree = mm_per_degree
        self.lower_step_limit = lower_step_limit
        self.upper_step_limit = upper_step_limit
        self.is_running = False
    
    async def go_to_step(self, steps): # takes an absolute position in steps and tries to go there
        self.is_running = True
        SECONDS_PER_STEP = .05 # this is overly slow, for testing
        if steps == self.ticks: return
        direction = stepper.FORWARD if steps > self.ticks else stepper.BACKWARD
        # first of all, get to an integer number of steps
        whole_steps, decimal_steps = divmod(self.ticks, 1)
        microsteps_needed = ((1.0-decimal_steps)/16.0) if direction == stepper.FORWARD else (decimal_steps/16.0)
        self.logger.debug(f"Need {microsteps_needed} microsteps then {whole_steps} whole steps {'forward' if direction == stepper.FORWARD else 'backward'}")
        for i in range(microsteps_needed):
            self.stepper.onestep(direction=direction, style=stepper.MICROSTEP)
            self.ticks += (1 if direction == stepper.forward else -1) * 1/16
            await asyncio.sleep(SECONDS_PER_STEP)
        # now normal steps
        assert self.ticks - int(self.ticks) == 0, "position should be a whole number"
        for i in range(abs(whole_steps - int(self.ticks))):
            self.stepper.onestep(direction=direction, style=stepper.DOUBLE)
            self.ticks += 1 if direction == stepper.forward else -1
            await asyncio.sleep(SECONDS_PER_STEP)
        self.is_running = False
    
    async def go_to_position(self, position):
        steps_needed = self.mm_per_degree * self.degrees_per_tick * position
        # round to nearest 16th
        partial = steps_needed % (1/16)
        if partial < 1/16/2:
            steps_needed -= partial
        else:
            steps_needed += (1/16)-partial
        await self.go_to_step(steps_needed)
    
    def redefine_position(self, new_position):
        if self.is_running:
            return False # could not change position while motor is running
        self.position = new_position
        return True
        