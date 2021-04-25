from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
board = env.BoardConfig()

if board.get("build.bsp.name", "nrf5") == "adafruit":
    env.SConscript("arduino/adafruit.py")
else:
    env.SConscript("arduino/nrf5.py")
