import os
import time

def create_fifo(path):
	try:
		os.mkfifo(path)
	except FileExistsError:
		pass

def create_disk(filename):
	if os.path.exists(filename):
		os.remove(filename)

	os.system(f"qemu-img create -f qcow2 {filename} 496M")

def send_monitor(command):
	with open("/tmp/guest.in", "w") as f:
		f.write(f"{command}\n")

def change_floppy(path):
	send_monitor(f"change floppy0 \"{path}\" raw")
	time.sleep(5)

def wait():
	print("Please type enter to continue...")
	input()