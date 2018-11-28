#!/usr/bin/python3.6

from ast import literal_eval
import time
import socket
import re
import sys
##custom libs
from lib.conn_manager import ConnManager
from lib.br_manager import BrowserManager
from lib.gw_manager import GwManager



def main():
	conf_manager = None
	container_type = None
	hostname = socket.gethostname()
	configs_dir = sys.argv[1]
	
	if re.search(r'conn', hostname, re.I|re.S):
		conf_manager = ConnManager()
	elif re.search(r'br', hostname, re.I|re.S):
		conf_manager = BrowserManager(configs_dir)		
	elif re.search(r"gw", hostname, re.I|re.S):
		conf_manager = GwManager(configs_dir)
	print("loaded_json BEFORE endless loop => {}".format(conf_manager.loaded_json))
	while True:
		print("Checking config status in ETCD")
		conf_manager.check_config_status()
		conf_manager.check_platform_status()
		print("Sleeping for 20 seconds")
		time.sleep(20)

main()