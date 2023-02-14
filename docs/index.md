# About This Document
This is a piece of documentation written by two people, Lucia Whitmore @lwhitmo and River Lewis @rivques. We have each roughly written about the parts of the project we worked on, and this is denoted by the heading of a section being followed by "- NAME." If there is no heading suffix, we have both written/worked on the section.
# Assignment
For this assignment, we had to build a robot arm. To narrow down the endless possibilities, every student in the class came up with a problem or two they wanted to solve with a robotic arm and pitched it to the rest of the class. People picked projects they thought looked interesting, and groups of two were formed. Our group wanted to create a robotic arm to automate the process of programming music boxes. This is done by punching holes in a paper tape to indicate notes and timing. We opted to use a gantry, as we had very independent orthogonal axes (X is note, Y is time, Z is punching axis) and wanted rigidity and accuracy.
# Parts
- Metro M4 Airlift Lite
- 2 NEMA-17 stepper motors
- 2 micro servo motors
- 2 DRV8833 H-bridges
- 1 TT motor
- 1 NPN transistor
- 1 diode
- 1 full-sized breadboard
- 1 3/32" drill bit
- roughly 250 mm of 2020 aluminum extrusion
- 4 rubber bands
- 4 V-rollers and related hardware
- OpenBuilds stepper mount plate
- OpenBuilds idler mount plate
- assorted hookup wire
- assorted fasteners
- 3D printed parts
# CAD - Lucia
!TODO: Screenshots here
!TODO: Talk about specific interesting parts
# Circuit
!TODO: Fritzing here
# Code - River
The full code is available [here](https://github.com/rivques/AutoMusicBoxHolePuncher). Interesting parts will be discussed below.
## MIDI to Music Box
Fortunately for us, somebody else had already [made a project like this](https://jshel.co/blog/music-box-hole-punch) and created [a piece of software](https://drive.google.com/drive/folders/0B1Z6_pBGv9-FMFFUNTI3YkFLVXM) that could take in a MIDI file, automatically do a bunch of error checking, and spit out instructions for a robot like ours like `PUNCH NOTE 12` or `ADVANCE PAPER 12300`. This saved an enormous amount of time learning the MIDI protocol.
## Async
I knew from the start this program would be asynchronous, as I wanted to run both a user interface and the robot itself at the same time. With that in mind, I separated the code into a few main components: A UI function that would update the terminal as needed, a hole punching function that would iterate over instructions and execute them, a few helper functions to parse the instruction file, and a state machine to tie it all together.
### Async input
One of the more interesting problems I ran into was that of taking user input asynchronously. I needed a coroutine that I could `await` that would return when the user had entered input but allow other tasks to happen while waiting on the input. I eventually ended up doing this by polling `supervisor.runtime.serial_bytes_available`, which is `True` when there is data waiting on the serial line, and calling `await asyncio.sleep(0)` while there was nothing to allow other tasks to run.
## Memory issues (in Python! what fun!)
While figuring out how to make the TUI continuously update, I started running into hard-to-pin-down `MemoryErrors`. After generous logging (which somewhat exacerbated the issue, because `logging` records take up memory even if they aren't printed) and digging through the `asyncio`'s code, I realized the issues stemmed from my use of `asyncio.run()`, like this:
```python
async def run_ui(self):
    # ...
    await asyncio.sleep(.25)
    asyncio.run(self.run_ui())
    return
```
It turns out that this recursion (which felt really clever at the time of writing) was causing the issues. Every time I called `asyncio.run()`, an entry would be added to a stack inside of `asyncio`. However, because `run()` blocks until it returns, older recursions of `run_ui()` would never return (because they weer waiting on their children, which were waiting on their children, etc.). This caused a buildup of entries on that stack, which would eventually fill up the (small) memory on the Metro and throw a MemoryError. The solution ended up being to use an outside loop to run the function instead of using recursion:
```python
async def run_ui_forever(self):
        while True:
             await holePuncher.run_ui()
```
...which can be run with a single `asyncio.create_task()` in the main program, avoiding the recursion issue. In retrospect it seems fairly obvious that it's a bad idea to *recurse a purposefully infinite loop*, but in the moment I saw an opportunity for recursion, thought "ooh! I can use a cool CS trick!" and didn't think too much more about it (until I spent hours later staring at it, of course).
## Stepper control
I made my own stepper controller for this project. I needed a controller that could asynchronously run to any given position in millimeters (internally handling the math to go between linear millimeters and rotational steps). The Adafruit stepper library only offered the capability to make a single step (or microstep) in a given direction, so I built a controller around this. I originally attempted to include microstepping, but I ran into trouble with it and it turned out we were accurate to something like .18 mm with whole steps, which is more than enough for this application.
## Text user interface
I made a TUI that shows the progress through the current file, the currently executing instruction, and the motor positions without spamming the serial log. I do this by recording the length of the last printed line, then deleting it and writing the current state in its place. One quirk I ran into is that transmitting the backspace character `\b` doesn't actually delete the previous character, it just moves the cursor back over it. Because of this, in order to send a line, I:
1. Send as many backspace characters as there were characters in the last message.
2. Send as many space characters as there were characters in the last message, to overwrite it.
3. Re-send the backspaces to get back to the start of the line.
4. Construct the new status string and record its length for the next iteration.
5. Send the new status string, making sure to end with the empty string `''` and not the default newline `\n`.
# Fabrication - Lucia
## The carriage
!TODO: talk about eccentric nuts, V-roller assembly
## The drill bit
!TODO: FLIR image of drill bit heating
# Results
We ultimately ran out of time to complete the project. We were very close, but our final product at the deadline wasn't able to actually drill through the paper. That said, we built an accurate X carriage on V-rollers, a multitasking controller, a paper feeder, and a (weak) endmill.
![Here's how you make an image, describe the image here](docs/auto-music-box/path-to-image.jpg "Caption for the image here")
# Reflection and Lessons Learned
## SO MANY PRINTS
We ended up printing an enourmous number of prototypes, mostly for the carriage. About half of these were used to develop code with while waiting for more design work to get done and the other half were instantly scrapped after a design flaw became clear. Most of these flaws were based on forgetting that hardware can't magically appear in its position (and that said hardware usually needs a way for a screwdriver to get at it). On the next project we design, we have learned the hard way to think about how a part is going to get where it needs to be before putting it somewhere.
## Scheduling
We set a nice schedule for this project at the beginning, but weren't able to stick to it. This was mostly because the designs for the proof of concept took far longer than anticipated, and ate up about 3 weeks of time. This may have been because we tried to dive into CAD and hope things worked themselves out instead of first planning out exactly what would be going on on paper.
## Integration Hell
Integration Hell is where you are when you are fixing all the problems that happen when different subassemblies are put together. It's an inevitability on any project and, while the problems are surmountable, they take time to fix. Because of the previously mentioned scheduling difficulties, we only had a few hours of time with the project fully assembled (instead of the *month* our schedule anticipated). As a result, we ran into a design flaw and were only able to make one (unsuccessful and rushed) attempt at fixing it. The root cause of this is probably both the overly optimistic schedule and only starting to put in extra time to try to stay vaguely on top of things very late in the project.
## A Side Quest - River
In fabricating the rollers for this project, I realized I had a perfect opportunity to [explore arc overhangs](https://rivques.github.io/other-random-projects/fun-with-overhangs/), which are a method of 3D printing over thin air when it would otherwise be impossible. Ultimately we didn't end up using the result of this endeavor because I couln't get the tuning right for the very large rollers we needed, but it was a fun tangent to explore.