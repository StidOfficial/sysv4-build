#!/usr/bin/python3
import os
import shutil
import sys
import time
import pexpect
from shared import *

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

child = pexpect.spawn(f"qemu-system-i386 -m 192 -hda {DISK_PATH} \
			-monitor pipe:{MONITOR_PIPE_PATH} -display curses",
			encoding="utf-8", timeout=100)
child.logfile = sys.stdout

login(child)

child.sendline("echo \"s1:12345:respawn:/etc/getty tty00 9600 none LDISC0\" >> /etc/inittab")
time.sleep(10)

child.sendline("sed \"s/console/tty00/g\" /etc/default/login > /etc/default/login.bak")
child.sendline("mv /etc/default/login.bak /etc/default/login")
time.sleep(10)

child.sendline("cd /; shutdown -g0 -y")

child.expect("Reboot the system now.")
send_monitor("quit")

child.wait()

shutil.move(DISK_PATH, ".")