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
    motor_logger = adafruit_logging.getLogger("motor")
    
    _hole_puncher_state = "OFF"

    # hardware
    raw_stepper = StepperMotor(PWMOut(board.D2, frequency=2000), PWMOut(board.D3, frequency=2000), PWMOut(board.D4, frequency=2000), PWMOut(board.D5, frequency=2000))
    x_stepper = StepperController(raw_stepper)
    y_stepper = StepperController(StepperMotor(PWMOut(board.D6, frequency=2000), PWMOut(board.D7, frequency=2000), PWMOut(board.D8, frequency=2000), PWMOut(board.D9, frequency=2000)))
    z_servo_a = Servo(PWMOut(board.SDA, duty_cycle=2 ** 15, frequency=50), min_pulse=500, max_pulse=2500)
    z_servo_b = Servo(PWMOut(board.A5, duty_cycle=2 ** 15, frequency=50), min_pulse=500, max_pulse=2500)
    drill_motor = PWMOut(board.D11)
    
    # punching state for ui
    num_operations = 0
    operation_num = 0
    last_string_len = 0
    need_ui_update = False
    running_filename = ""

    @property
    def hole_puncher_state(self):
        return self._hole_puncher_state
    
    @hole_puncher_state.setter
    def hole_puncher_state(self, newValue):
        # here's the on state change code
        if newValue == "OFF":
            print("Goodbye!")
            asyncio.get_event_loop().stop()
        elif newValue == "STARTUP":
            pass
        elif newValue == "IDLE":
            pass
        elif newValue == "PUNCHING":
            self.num_operations = 0
            self.operation_num = 0
            self.last_string_len = 0
            self.need_ui_update = True
        else:
            raise ValueError(f"Unknown state value! Must be one of OFF, STARTUP, IDLE, PUNCHING")
        self._hole_puncher_state = newValue

    def __init__(self) -> None:
        self.logger.setLevel(adafruit_logging.DEBUG)
        self.motor_logger.setLevel(adafruit_logging.INFO)
        self.hole_puncher_state = "STARTUP"

    async def run_ui(self):
        # ui loop, will call itself again if it's still turned on
        if self.hole_puncher_state == "OFF":
            return
        elif self.hole_puncher_state == "STARTUP":
            print("Welcome to the Automatic Music Box Hole Puncher!")
            self.hole_puncher_state = "IDLE"
        elif self.hole_puncher_state == "IDLE":
            try:
                filename = await ainput("Please enter a filename to print, or hit Ctrl-C to quit: ")
            except KeyboardInterrupt:
                sys.stdout.write("\n")
                self.hole_puncher_state = "OFF"
                return
            self.hole_puncher_state = "PUNCHING"
            self.running_filename = filename
            asyncio.create_task(self.punch_holes(self.parse_file(filename)))
        elif self.hole_puncher_state == "PUNCHING":
            # cool UI stuff here
            while not self.need_ui_update:
                await(asyncio.sleep(0))
            self.need_ui_update = False
            # delete what we wrote last
            print("\b" * self.last_string_len, end="")
            # compose this status update
            status_string = f"Printing {self.running_filename}, instruction {self.operation_num}/{self.num_operations}"
            self.last_string_len = len(status_string)
            print(status_string, end="")

        asyncio.run(self.run_ui())
        
    def parse_file(self, file):
        # parse a txt file of a song and return a list of Operations
        return [Operation("PROGRAMSTART", 0), Operation("ADVANCEPAPER", 1000), Operation("PUNCHNOTE", 20), Operation("ADVANCEPAPER", 10000), Operation("PROGRAMEND", 0)]
    
    async def punch_holes(self, operations):
        self.y_stepper.redefine_position(0)
        # given a list of Operations, execute them
        self.num_operations = len(operations)
        for operation_num, operation in enumerate(operations):
            self.operation_num = operation_num
            # again, rust match would be so nice here
            if operation.operationType == "PROGRAMSTART":
                pass
            elif operation.operationType == "PROGRAMEND":
                print(f"Finished song!")
                self.hole_puncher_state = "IDLE"
                return
            elif operation.operationType == "PUNCHNOTE":
                pass
            elif operation.operationType == "ADVANCEPAPER":
                await self.y_stepper.go_to_position(operation.operationValue / 1000) # operationValue is in microns, position is in mm

if __name__ == "__main__":
    holePuncher = HolePuncher()
    asyncio.run(holePuncher.run_ui())
    asyncio.get_event_loop().run_forever()