#!/usr/bin/python3
import os
import sys
import pexpect

def create_fifo(path):
	try:
		os.mkfifo(path)
	except FileExistsError:
		pass

def send_monitor(command):
	with open("/tmp/guest.in", "w") as f:
		f.write(f"{command}\n")

def wait():
	print("Please type enter to continue...")
	input()

def reboot(child):
	child.expect("Reboot the system now.")
	send_monitor("system_reset")

create_fifo("/tmp/guest.in")
create_fifo("/tmp/guest.out")
create_fifo("/tmp/test")

child = pexpect.spawn("qemu-system-i386 -m 192 -hda /tmp/primary.qcow2 -hdb /tmp/secondary.qcow2 -monitor pipe:/tmp/guest -display curses")
child.logfile = sys.stdout.buffer

child.expect("Console Login:")
child.sendline("root")

child.expect("Password:")
child.sendline("")

child.sendline("diskadd 1")

child.expect("\(Strike y or n followed by ENTER\)")
child.sendline("y")

child.expect("To select this, please type \"y\".")
child.sendline("y")

child.expect("You will now be queried on the setup of your disk.")
child.sendline("1")

child.expect("Please enter the absolute pathname \(e.g., /usr3\) for")
child.sendline("/src")

child.sendline("ufs")
child.sendline("y")
child.sendline("y")

child.expect("Disksetup completed.")
child.sendline("shutdown -g0 -y")

child.expect("Reboot the system now.")
send_monitor("quit")

child.wait()