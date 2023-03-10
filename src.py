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
FLOPPIES_DIR="Intel Unix SVR4V2 (5.25 Floppy)"

for type in ["in", "out"]:
	create_fifo(f"{MONITOR_PIPE_PATH}.{type}")

child = pexpect.spawn(f"qemu-system-i386 -m 192 -fda src/xaa -hda {DISK_PATH} \
			-monitor pipe:{MONITOR_PIPE_PATH} -display curses",
			encoding="utf-8", timeout=100)
child.logfile = sys.stdout

login(child)

run_command(child, "/etc/conf/bin/idtune NINODE 1300")
run_command(child, "/etc/conf/bin/idtune NS5INODE 1300")
run_command(child, "/etc/conf/bin/idtune UFSNINODE 1300")
run_command(child, "/etc/conf/bin/idtune SFSZLIM 0x7FFFFFFF")
run_command(child, "/etc/conf/bin/idtune HFSZLIM 0x7FFFFFFF")

child.sendline("/etc/conf/bin/idbuild")
child.expect("The UNIX Kernel has been rebuilt.")

run_command(child, "sed \"/ULIMIT/d\" /etc/default/login > /etc/default/login.new")
run_command(child, "mv /etc/default/login.new /etc/default/login")

child.sendline("/etc/conf/bin/idreboot")

child.expect("Strike ENTER when ready")
child.sendline()

reboot(child)

login(child)

child.sendline("pkgadd -d diskette1")

install_package(child, f"{FLOPPIES_DIR}/Intel Unix System V R4.0 V2.0 - Disk 43 - Development Set - scde - C Development Environment - Disk 1 of 3.img")
install_next_package(child, f"{FLOPPIES_DIR}/Intel Unix System V R4.0 V2.0 - Disk 44 - Development Set - scde - C Development Environment - Disk 2 of 3.img")
install_next_package(child, f"{FLOPPIES_DIR}/Intel Unix System V R4.0 V2.0 - Disk 45 - Development Set - scde - C Development Environment - Disk 3 of 3.img")

child.expect("Type \[go\] when ready,")
child.sendline("q")

for file in sorted(os.listdir("src/")):
	file_path=f"src/{file}"

	if file.startswith("xa"):
		change_floppy(file_path)

		ibs=4096
		file_size=os.path.getsize(file_path)

		if file_size < 1474560:
			ibs=1

		run_command(child, f"dd if=/dev/rdsk/f0t of=/tmp/{file} ibs={ibs} count={file_size}")

run_command(child, "cat /tmp/xa? > /sysvr4.tar.Z")
run_command(child, "uncompress /sysvr4.tar.Z")
run_command(child, "ROOT=/usr/src386; export ROOT")
run_command(child, "mkdir -p $ROOT/usr; cd $ROOT/usr")
child.sendline(f"tar xf /sysvr4.tar; echo exit:$?")
child.expect("exit:")
run_command(child, "mv svr4 src")

shutdown(child)

send_monitor("quit")

child.wait()

shutil.copy(DISK_PATH, ".")