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

def shutdown(child):
	child.sendline("cd /; shutdown -g0 -y")
	child.expect("Reboot the system now.")

def reboot(child):
	child.expect("Reboot the system now.")
	send_monitor("eject floppy0")
	send_monitor("system_reset")

def install_next_package(child, path):
	child.expect("Type \[go\] when ready,")
	change_floppy(path)

	child.sendline("go")

def install_package(child, path):
	install_next_package(child, path)

	child.expect("Select package\(s\) you wish to process")
	child.sendline("")

def run_command(child, line):
	child.sendline(f"{line}; echo exit:$?")
	child.expect("exit:0")