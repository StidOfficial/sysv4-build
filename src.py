#!/usr/bin/python3
import os
import sys
import time
import pexpect
from shared import *

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

DISK_PATH="/tmp/sysv.qcow2"
MONITOR_PIPE_PATH="/tmp/guest"

for type in ["in", "out"]:
	create_fifo(f"{MONITOR_PIPE_PATH}.{type}")

child = pexpect.spawn(f"qemu-system-i386 -m 192 -fda src/xaa -hda {DISK_PATH} \
			-monitor pipe:{MONITOR_PIPE_PATH} -display curses",
			encoding="utf-8", timeout=100)
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

for file in sorted(os.listdir("src/")):
	file_path=f"src/{file}"

	if file.startswith("xa"):
		change_floppy(file_path)

		ibs=4096
		file_size=os.path.getsize(file_path)

		if file_size < 1474560:
			ibs=1

		child.sendline(f"dd if=/dev/rdsk/f0t of=/dev/{file_path} ibs={ibs} count={file_size}")

		child.expect("records out")

child.sendline("cat /dev/xa? > sysvr4.tar.Z")
time.sleep(10)

child.sendline("uncompress sysvr4.tar.Z")
time.sleep(10)

child.sendline("cd /; shutdown -g0 -y")

child.expect("Reboot the system now.")
send_monitor("quit")

child.wait()