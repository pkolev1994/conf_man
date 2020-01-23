#!/usr/bin/python3.4

from ast import literal_eval
import time
import socket
import re
import sys
##custom libs
sys.path.append('/aux0/customer/containers/ocpytools/lib/')
from logger import Logger

sys.path.append('/aux0/customer/containers/occonfman/')
from lib.conn_manager import ConnManager
from lib.br_manager import BrowserManager
from lib.gw_manager import GwManager
from lib.rest_manager import RestAppManager




def main():
	logger = Logger(filename = "occonfman", \
				logger_name = "manager.py main", \
				dirname="/aux1/occonfman/logs/")

	logger.info("Starting conf_manager ...")
	conf_manager = None
	container_type = None
	hostname = socket.gethostname()
	configs_dir = None
	if len(sys.argv) > 1:
		configs_dir = sys.argv[1]
	
	if re.search(r'conn', hostname, re.I|re.S):
		conf_manager = ConnManager()
		logger.info("Initializing connector manager")
	elif re.search(r'br', hostname, re.I|re.S):
		conf_manager = BrowserManager(configs_dir)
		logger.info("Initializing browser manager")	
	elif re.search(r"gw", hostname, re.I|re.S):
		conf_manager = GwManager(configs_dir)
		logger.info("Initializing gw manager")
	else:
		conf_manager = RestAppManager()
		logger.info("Initializing RestAppManager manager")
	logger.clear_handler()
	while True:
		# print("Checking config status in ETCD")
		conf_manager.check_config_status()
		conf_manager.check_platform_status()
		# print("Sleeping for 20 seconds")
		time.sleep(4)

main()