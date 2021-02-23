Import("env")
import shutil
import os

# print(env)
print("POST")
# print(env.Dump())

firmware_source = os.path.join(env.subst("$BUILD_DIR"), "firmware.hex")
firmware_folder = os.path.join(env.subst("$BUILD_DIR"), "..", "firmware.hex")

print(firmware_folder)

def after_build(source, target, env):
	shutil.copy(firmware_source, firmware_folder)

env.AddPostAction ("buildprog", after_build)

