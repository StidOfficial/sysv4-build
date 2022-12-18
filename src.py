#!/usr/bin/python3
import os
import sys
import time
import pexpect

def create_fifo(path):
	try:
		os.mkfifo(path)
	except FileExistsError:
		pass

def send_monitor(command):
	with open("/tmp/guest.in", "w") as f:
		f.write(f"{command}\n")

def change_floppy(path):
	send_monitor(f"change floppy0 \"{path}\" raw")

def wait():
	print("Please type enter to continue...")
	input()

def reboot(child):
	child.expect("Reboot the system now.")
	send_monitor("eject floppy0")
	send_monitor("system_reset")

def login(child):
	child.expect("Console Login:")
	child.sendline("root")

	child.expect("Password:")
	child.sendline("")

	child.sendline("")

	child.expect("you have mail")

create_fifo("/tmp/guest.in")
create_fifo("/tmp/guest.out")
create_fifo("/tmp/test")

child = pexpect.spawn("qemu-system-i386 -m 192 -fda xaa -hda /tmp/primary.qcow2 -monitor pipe:/tmp/guest -display curses", encoding="utf-8")
child.logfile = sys.stdout

login(child)

child.sendline("/etc/conf/bin/idtune NINODE 1300")
time.sleep(2)

child.sendline("/etc/conf/bin/idtune NS5INODE 1300")
time.sleep(2)

child.sendline("/etc/conf/bin/idtune UFSNINODE 1300")
time.sleep(2)

child.sendline("/etc/conf/bin/idtune SFSZLIM 0x7FFFFFFF")
time.sleep(2)

child.sendline("/etc/conf/bin/idtune HFSZLIM 0x7FFFFFFF")
time.sleep(2)

child.sendline("/etc/conf/bin/idbuild")
child.expect("The UNIX Kernel has been rebuilt.")

child.sendline("sed \"/ULIMIT/d\" /etc/default/login > /etc/default/login.new")
time.sleep(2)

child.sendline("mv /etc/default/login.new /etc/default/login")
time.sleep(2)

child.sendline("/etc/conf/bin/idreboot")
time.sleep(2)

child.expect("Strike ENTER when ready")
child.sendline()

reboot(child)

login(child)

for file in sorted(os.listdir()):
	if file.startswith("xa"):
		change_floppy(file)

		ibs=4096

		if os.path.getsize(file) < 1474560:
			ibs=1

		child.sendline(f"dd if=/dev/rdsk/f0t of=/dev/{file} ibs={ibs} count={os.path.getsize(file)}")

		child.expect("records out", timeout=100)

child.sendline("cat /dev/xa? > sysvr4.tar.Z")
time.sleep(5)

child.sendline("uncompress sysvr4.tar.Z")

child.sendline("cd /; shutdown -g0 -y")

child.expect("Reboot the system now.")
send_monitor("quit")

child.wait()

child.logfile = None

print("Switch to interect mode")
child.interact()