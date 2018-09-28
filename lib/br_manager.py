import os

###custom libs
from lib.etcd_client import EtcdManagement
from lib.conf_tools import update_conf_json
from lib.conf_tools import parse_conf_json
from lib.conf_tools import md5





class BrowserManager():

	def __init__(self):
		"""
		Constructor
		Args:
			None
		Returns:
			None
		"""
		self.config_file = "/aux0/customer/ocbrowser/etc/ocbrowser.xml"
		self.conf_manager_file = "/home/pkolev/Containers/conf_manager/conf_manager.json"
		


	def check_config_status(self):
		"""
		Makes md5 of curr config and 
		and diff it with the  md5 from
		self.browser_file
		Args:
			None
		Returns:
			None
		"""

		loaded_md5_conf = parse_conf_json(self.conf_manager_file)["md5"]
		curr_md5_conf = md5([self.config_file])
		if loaded_md5_conf != curr_md5_conf:
			update_conf_json(json_file = self.conf_manager_file, \
				state= 'add', \
				key= 'md5', \
				value=curr_md5_conf)
			self.reload()
			print("Connectors are restarted!!!")



	@staticmethod
	def reload():
		"""
		Reloads application
		Args:
			None
		Returns:
			None
		"""
		os.system("ocbrowser reload")
