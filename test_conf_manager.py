from ast import literal_eval
import time
import socket
import re
##custom libs
from lib.conn_manager import ConnManager
from lib.br_manager import BrowserManager
from lib.etcd_client import EtcdManagement


def main():
	# hostname= re.search(r'(.*?)\_conn', socket.gethostname(), re.I|re.S).group(1)
	####simulating
	conf_manager = None
	container_type = None
	hostname = None
	hostname = "br_11"
	etcd_manager = EtcdManagement()
	# if re.search(r'conn', socket.gethostname(), re.I|re.S):
	if re.search(r'conn', hostname, re.I|re.S):
		container_type = 'connector'
		# hostname= re.search(r'(.*?)\_conn', socket.gethostname(), re.I|re.S).group(1)
		hostname= re.search(r'(.*?)\_conn', hostname, re.I|re.S).group(1)
		conf_manager = ConnManager()
	# elif re.search(r'br', socket.gethostname(), re.I|re.S):
	elif re.search(r'br', hostname, re.I|re.S):
		container_type = 'browser'
		hostname = 'br'
		conf_manager = BrowserManager()		

	while True:
		print("Getting platform status from etcd... ")
		platform_status = etcd_manager.get_platform_status()
		print("Platform status => {}".format(platform_status))
		if container_type == 'connector' and hostname == "smpp":
			new_browsers = conf_manager.get_new_browsers(literal_eval(platform_status))
			new_ussd_gws = conf_manager.get_new_ussd_gws(literal_eval(platform_status))
			conf_manager.update_configs(browsers = new_browsers, ussd_gws = new_ussd_gws)
			conf_manager.check_config_status()
		elif container_type == 'connector':
			new_browsers = conf_manager.get_new_browsers(literal_eval(platform_status))
			conf_manager.update_configs(browsers = new_browsers)
			conf_manager.check_config_status()
		elif container_type == 'browser':
			conf_manager.check_config_status()


		time.sleep(20)

main()