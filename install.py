#!/usr/bin/python3
import os
import shutil
import sys
import time
import pexpect

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

def wait():
	print("Please type enter to continue...")
	input()

def reboot(child):
	child.expect("Reboot the system now.")
	send_monitor("eject floppy0")
	send_monitor("system_reset")

def password(child):
	child.expect("Enter a password for the")
	child.sendline()
	child.expect("New password:")
	child.sendline()

def install_package(child, path):
	child.expect("Type \[go\] when ready,")
	change_floppy(path)
	time.sleep(2)

	child.sendline("go")

	child.expect("Select package\(s\) you wish to process")
	child.sendline("")

FLOPPIES_DIR="AT&T UNIX System V Release 4 Version 2.1 (3½)"
DISK_PATH="/tmp/sysv.qcow2"
MONITOR_PIPE_PATH="/tmp/guest"

for type in ["in", "out"]:
	create_fifo(f"{MONITOR_PIPE_PATH}.{type}")

create_disk(DISK_PATH)

child = pexpect.spawn(f"qemu-system-i386 -m 192 -fda \"{FLOPPIES_DIR}/Base 01 (2.1a).img\" \
			-hda {DISK_PATH} -monitor pipe:{MONITOR_PIPE_PATH} -display curses")
child.logfile = sys.stdout.buffer

child.expect("Floppy Disk 2 and then strike ENTER.")
change_floppy(f"{FLOPPIES_DIR}/Base 02 (2.1a).img")
child.sendline()

child.expect("Please strike ENTER to install the UNIX System")
child.sendline()

child.expect("WARNING: A new installation of the UNIX System will destroy")
# Do you wish to continue (y or n)?
child.sendline("y")

child.expect("You are about to partition hard disk 0.")
# Please strike ENTER when ready or DEL to cancel the installation.
child.sendline()

child.expect("differently, type \"n\" and the \"fdisk\" program will let you")
# disk slices or filesystems (y or n)?
child.sendline("y")

child.expect("Please select the File System Type for /")
# Please press ENTER for the default type, ufs.
child.sendline()

child.expect("Do you wish to create any optional")
# disk slices or filesystems (y or n)? 
child.sendline("n")

time.sleep(1)

# Is this correct (y or n)?
child.sendline("y")

time.sleep(1)

# Please strike ENTER to continue or DEL to cancel the installation.
child.sendline()

time.sleep(2)

# Is this configuration acceptable?
child.sendline("y")

reboot(child)

child.expect("or \"F\" to install from FLOPPY DISKETTE.")
# Strike ESC to stop.
child.sendline("F")

for i in range(3, 11):
	child.expect("Please insert the UNIX System \"Base System Package\"")

	change_floppy(f"{FLOPPIES_DIR}/Base {i:02}.img")
	time.sleep(2)

	child.sendline()

	time.sleep(10)

password(child)
password(child)
password(child)

child.expect("Please enter a System Name for this system.")
child.sendline("VM")

child.expect("Strike ENTER when ready.")
change_floppy(f"{FLOPPIES_DIR}/Maintenance 1.img")
time.sleep(2)

child.sendline()

child.expect("Select package\(s\) you wish to process")
child.sendline("all")

child.expect("Insert diskette 2 of 2 into Floppy Drive 1")
change_floppy(f"{FLOPPIES_DIR}/Maintenance 2.img")
child.sendline("go")

child.expect("Strike ENTER when ready.")
child.sendline()

reboot(child)

child.expect("Console Login:")
child.sendline("root")

child.expect("Password:")
child.sendline("")

child.sendline("")
child.sendline("")

child.sendline("pkgadd -d diskette1")

install_package(child, f"{FLOPPIES_DIR}/Editing Utilities.img")
install_package(child, f"{FLOPPIES_DIR}/Remote Terminal Package.img")
child.expect("Install terminfo file\(s\)")
child.sendline("1")
child.sendline("all")
child.expect("Terminate installation")
child.sendline("0")

install_package(child, f"{FLOPPIES_DIR}/FMLI Package.img")
install_package(child, f"{FLOPPIES_DIR}/Networking Support Utility Package.img")
child.sendline("")
install_package(child, f"{FLOPPIES_DIR}/OA&M Basic & Ext. 1.img")
child.sendline("")
time.sleep(2)

child.sendline("")
time.sleep(2)

# New password:
child.sendline("")
child.sendline("")
time.sleep(2)

child.expect("Type \[go\] when ready,")
change_floppy(f"{FLOPPIES_DIR}/OA&M Basic & Ext. 2.img")
time.sleep(2)

child.sendline("go")

child.expect("Type \[go\] when ready,")
change_floppy(f"{FLOPPIES_DIR}/OA&M Basic & Ext. 3.img")
time.sleep(2)

child.sendline("go")

install_package(child, f"{FLOPPIES_DIR}/FACE Package.img")

child.sendline("q")

child.sendline("shutdown -g0 -y")

child.expect("Reboot the system now.")
send_monitor("quit")

child.wait()

shutil.move(DISK_PATH, ".")