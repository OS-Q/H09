from os import listdir
from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("A41B")
assert isdir(FRAMEWORK_DIR)

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CFLAGS=["-std=gnu11"],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-Wall",
        "-mthumb",
        "-nostdlib",
        "--param", "max-inline-insns-single=500"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions",
        "-std=gnu++11",
        "-fno-threadsafe-statics"
    ],

    CPPDEFINES=[
        ("ARDUINO", 10805),
        # For compatibility with sketches designed for AVR@16 MHz (see SPI lib)
        ("F_CPU", "16000000L"),
        "ARDUINO_ARCH_NRF5",
        "NRF5",
        "%s" % board.get("build.mcu", "")[0:5].upper()
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "toolchain", "gcc")
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", board.get("build.core")),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "drivers_nrf", "delay"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "device"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "toolchain"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "toolchain", "CMSIS", "Include")
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections",
        "-mthumb",
        "--specs=nano.specs",
        "--specs=nosys.specs",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align"
    ],

    LIBSOURCE_DIRS=[join(FRAMEWORK_DIR, "libraries")],

    LIBS=["m"]
)

if "BOARD" in env:
    env.Append(
        CCFLAGS=[
            "-mcpu=%s" % env.BoardConfig().get("build.cpu")
        ],
        LINKFLAGS=[
            "-mcpu=%s" % env.BoardConfig().get("build.cpu")
        ]
    )

if board.get("build.cpu") == "cortex-m4":
    env.Append(
        CCFLAGS=[
            "-mfloat-abi=softfp",
            "-mfpu=fpv4-sp-d16"
        ],
        LINKFLAGS=[
            "-mfloat-abi=softfp",
            "-mfpu=fpv4-sp-d16"
        ]
    )

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:]
)

# Process softdevice options
softdevice_ver = None
ldscript_path = None
cpp_defines = env.Flatten(env.get("CPPDEFINES", []))
if "NRF52_S132" in cpp_defines:
    softdevice_ver = "s132"
elif "NRF51_S130" in cpp_defines:
    softdevice_ver = "s130"
elif "NRF51_S110" in cpp_defines:
    softdevice_ver = "s110"

if softdevice_ver:

    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "cores", board.get("build.core"),
                 "SDK", "components", "softdevice", softdevice_ver, "headers")
        ],

        CPPDEFINES=["%s" % softdevice_ver.upper()]
    )

    hex_path = join(FRAMEWORK_DIR, "cores", board.get("build.core"),
                    "SDK", "components", "softdevice", softdevice_ver, "hex")

    for f in listdir(hex_path):
        if f.endswith(".hex") and f.lower().startswith(softdevice_ver):
            env.Append(SOFTDEVICEHEX=join(hex_path, f))

    if "SOFTDEVICEHEX" not in env:
        print("Warning! Cannot find an appropriate softdevice binary!")

    # Update linker script:
    ldscript_dir = join(FRAMEWORK_DIR, "cores",
                        board.get("build.core"), "SDK",
                        "components", "softdevice", softdevice_ver,
                        "toolchain", "armgcc")
    mcu_family = board.get("build.arduino.ldscript", "").split("_")[1]
    for f in listdir(ldscript_dir):
        if f.endswith(mcu_family) and softdevice_ver in f.lower():
            ldscript_path = join(ldscript_dir, f)

    if not ldscript_path:
        print("Warning! Cannot find an appropriate linker script for the "
              "required softdevice!")

if not board.get("build.ldscript", ""):
    # if SoftDevice is not specified use default ld script from the framework
    env.Replace(LDSCRIPT_PATH=ldscript_path or board.get("build.arduino.ldscript", ""))

# Select crystal oscillator as the low frequency source by default
clock_options = ("USE_LFXO", "USE_LFRC", "USE_LFSYNT")
if not any(d in clock_options for d in cpp_defines):
    env.Append(CPPDEFINES=["USE_LFXO"])

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    env.Append(CPPPATH=[
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"))
    ])

    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "FrameworkArduinoVariant"),
            join(FRAMEWORK_DIR, "variants",
                 board.get("build.variant"))))

libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduino"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"))))

env.Prepend(LIBS=libs)
