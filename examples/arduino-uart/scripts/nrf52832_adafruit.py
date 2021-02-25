Import("env")
import shutil
import os

firmware_source = os.path.join(env.subst("$BUILD_DIR"), "firmware.bin")
firmware_sign = os.path.join(env.subst("$BUILD_DIR"), "firmware_signature.bin")

def after_build(source, target, env):
	isExists=os.path.exists('build')
	if not isExists:
		os.mkdir('build')
	shutil.copy(firmware_source, 'build/nrf52832_adafruit_firmware.bin')
	shutil.copy(firmware_sign, 'build/nrf52832_adafruit_signature.bin')

env.AddPostAction("buildprog", after_build)

