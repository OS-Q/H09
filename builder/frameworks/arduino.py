"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.
"""

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
board = env.BoardConfig()

if board.get("build.bsp.name", "nrf5") == "adafruit":
    env.SConscript("arduino/adafruit.py")
else:
    env.SConscript("arduino/nrf5.py")
