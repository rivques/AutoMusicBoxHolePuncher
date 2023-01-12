from lib.utils import * # pyright: reportShadowedImports=false
import asyncio
from adafruit_motor.stepper import StepperMotor
from adafruit_motor.servo import Servo
import sys
from pwmio import PWMOut
import board
import adafruit_logging
import re
import os
import gc

class HolePuncher:
    logger = adafruit_logging.getLogger()
    motor_logger = adafruit_logging.getLogger("motor")

    line_parsing_re = re.compile(r"(.*):(\d+)")
    
    _hole_puncher_state = "OFF"

    # hardware
    x_stepper = StepperController(StepperMotor(PWMOut(board.D2, frequency=2000), PWMOut(board.D3, frequency=2000), PWMOut(board.D4, frequency=2000), PWMOut(board.D5, frequency=2000)))
    y_stepper = StepperController(StepperMotor(PWMOut(board.D6, frequency=2000), PWMOut(board.D7, frequency=2000), PWMOut(board.D8, frequency=2000), PWMOut(board.D9, frequency=2000)))
    z_servo_a = Servo(PWMOut(board.SDA, duty_cycle=2 ** 15, frequency=50), min_pulse=500, max_pulse=2500)
    z_servo_b = Servo(PWMOut(board.A5, duty_cycle=2 ** 15, frequency=50), min_pulse=500, max_pulse=2500)
    drill_motor = PWMOut(board.D11)
    
    # punching state for ui
    num_operations = 0
    operation_num = 0
    operations = []
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
            print(f"\nFound files {', '.join([file for file in os.listdir()])}")
            good_filename = False
            while not good_filename:
                try:
                    filename = (await ainput("Please enter a filename to print, or hit Ctrl-C to quit: ")).strip()
                    open(filename).close() # check if it exists
                except KeyboardInterrupt:
                    sys.stdout.write("\n")
                    self.hole_puncher_state = "OFF"
                    return
                except OSError:
                    print("The file doesn't exist.", end=" ")
                else:
                    good_filename = True
            self.hole_puncher_state = "PUNCHING"
            self.running_filename = filename
            asyncio.create_task(self.punch_holes(self.parse_file(filename)))
        elif self.hole_puncher_state == "PUNCHING":
            # cool UI stuff here
            # compose this status update
            status_string = f"Printing {self.running_filename}, instruction {self.operation_num+1}/{self.num_operations}: {self.operations[self.operation_num]}, x: {self.x_stepper.get_position()}, y: {self.y_stepper.get_position()}, mem: {gc.mem_free()}, alloc: {gc.mem_alloc()}, task list len: ### "
            # delete what we wrote last
            sys.stdout.write("\b" * self.last_string_len)
            sys.stdout.write(" " * self.last_string_len) # \b only moves the cursor, need to overwrite with spaces to delete
            sys.stdout.write("\b" * self.last_string_len)
            sys.stdout.write(status_string)
            self.last_string_len = len(status_string)
        await asyncio.sleep(.25)
        return
        
    def parse_file(self, file):
        # parse a txt file of a song and return a list of Operations
        result = []
        with open(file) as f:
            for line in f.readlines():
                mo = self.line_parsing_re.match(line)
                if(mo is None):
                    self.logger.error(f"Failed to parse (no match) {line}")
                    continue
                result.append(Operation(mo.group(1), int(mo.group(2))))
        return result
    
    async def punch_holes(self, operations):
        self.y_stepper.redefine_position(0)
        # given a list of Operations, execute them
        self.operations = operations
        self.num_operations = len(operations)
        for operation_num, operation in enumerate(operations):
            self.operation_num = operation_num
            # again, rust match would be so nice here
            if operation.operationType == "PROGRAM START":
                pass
            elif operation.operationType == "PROGRAM END":
                self.hole_puncher_state = "IDLE"
                return
            elif operation.operationType == "PUNCH NOTE":
                await self.x_stepper.go_to_position(self.get_position_for_note(operation.operationValue))
                self.z_servo_a.angle = 45
                self.z_servo_b.angle = 135
                self.drill_motor.duty_cycle = 65535
                await asyncio.sleep(2)
                self.z_servo_a.angle = 90
                self.z_servo_b.angle = 90
                self.drill_motor.duty_cycle = 0
            elif operation.operationType == "ADVANCE PAPER":
                await self.y_stepper.go_to_position(operation.operationValue / 1000) # operationValue is in microns, position is in mm
            else:
                pass # probably got a metadata command, ignore it
        
    def get_position_for_note(self, note):
        return note*4 # placeholder
    
    async def run_ui_forever(self):
        while True:
             await holePuncher.run_ui()

if __name__ == "__main__":
    holePuncher = HolePuncher()
    asyncio.create_task(holePuncher.run_ui_forever())
    asyncio.get_event_loop().run_forever()