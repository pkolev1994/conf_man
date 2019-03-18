#!/usr/bin/env /usr/bin/python3.4
import sys
import os
import signal

option = sys.argv[1]
configs_dir = ""
if len(sys.argv) > 2:
	configs_dir = sys.argv[2]


def main():

	if option == "start":
		print("Starting manager ...")
		os.chdir("/aux0/customer/containers/occonfman/bin/")
		os.system("/usr/bin/python3.4 manager.py {} >/dev/null &".format(configs_dir))
	elif option == "stop":
		pstring = "manager.py"
		for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
			fields = line.split()
			pid = fields[0]
		print("Stopping manager ...")
		os.kill(int(pid), signal.SIGKILL)
	elif option == 'status':
		pstring = "manager.py"
		pid = None
		for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
			fields = line.split()
			pid = fields[0]
		if not pid:
			print("occonfman is not running: NO PID")
			return
		else:
			print("occonfman is running: {}".format(pid))	
	else:
		print("====================================================")
		print("Usage of occonfman : ")
		print("occonfman start/stop/status")
		print("====================================================")

main()