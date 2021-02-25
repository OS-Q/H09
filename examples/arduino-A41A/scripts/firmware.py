Import("env")
import shutil
import os

firmware_source = os.path.join(env.subst("$BUILD_DIR"), "firmware.bin")

def after_build(source, target, env):
	isExists=os.path.exists('build')
	if not isExists:
		os.mkdir('build')
	shutil.copy(firmware_source, 'build/arduino_A_nano33ble.bin')

env.AddPostAction("buildprog", after_build)

