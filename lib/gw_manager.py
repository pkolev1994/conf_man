#!/usr/bin/python3.4

import os
import re
import sys
from ast import literal_eval

###custom libs
sys.path.append('/aux0/customer/containers/occonfman/')
from lib.conf_manager import ConfManager
sys.path.append('/aux0/customer/containers/ocpytools/lib/')
from conf_tools import *


class GwManager(ConfManager):
	"""
	UssdGwManager class
	"""

	
	def __init__(self, local_configs):
		"""
		Constructor
		Args:
			None
		Returns:
			None
		"""
		super().__init__(local_configs)
		self.looking_browser = "{}_br".format(self.micro_platform)
		self.looking_gw = "{}".format(self.config_type)
		type_gw = re.search(r'\_gw\_(.*?$)', self.looking_gw, re.I|re.S).group(1).upper()
		self.conf_dir = "/aux0/customer/cross_plugin/{}/".format(type_gw)


	def etcd_file_updating(self, file_string, filename):
		"""
		Update key value in etcd structure
		in its hostname directory
		Args:
			file_string(str)
			filename(str)
		Returns:
			None
		"""
		super().etcd_file_updating(file_string, filename)


	def check_config_status(self):
		"""
		Args:
			None
		Returns:
			None
		"""
		super().check_config_status()


	def check_platform_status(self):


		logger = Logger(filename = "occonfman", \
						logger_name = "GwManager check_platform_status", \
						dirname="/aux1/occonfman/logs/")
		logger.info("Checking platform status ...")

		platform_state = self.etcd_manager.get_platform_status()
		new_md5_state = hash_md5(platform_state)
		if self.loaded_json['platform_state'] != new_md5_state:
			browsers = self.get_specific_apps(self.looking_browser)
			gws = self.get_specific_apps(self.looking_gw)
			if self.diff_browsers(browsers):
				etcd_config = self.etcd_manager.get_etcd_config()
				if self.etcd_manager.CheckExistAppType(self.config_type):
					confs = etcd_config["platform"][self.config_type]["general"]["confs"]
				else:
					return
				for config_name in confs:
					flag_id = "success"
					try:
						if re.search(r"(?:sip|map|cap)", self.hostname, re.I|re.S):
							account_id = re.search(r".*\.(\d+)$", gws[self.hostname], re.I|re.S).group(1)
							login = "{}{}".format( \
								re.search(r'.*\_(.*?)\_\d+', self.hostname, re.I|re.S) \
																.group(1).upper(), "GW")
							system_type = re.search(r'(.*?)GW', login, re.I|re.S).group(1)
							cross_cfg = self.generate_cfg_cross_plugin(browsers, account_id, login, system_type)
							generated_cfg = re.sub(r"(?is)<ipc>.*?<\/ipc>", "<ipc>{}</ipc>". \
											format(cross_cfg), confs[config_name])
							logger.info("Generating cfg => {}, with account_id => {}, login => {}, system_type => {}". \
										format(config_name, account_id, login, system_type))							
							r = re.compile(r"\$\{([^\}]+)\}")
							host_specific_markers = r.findall(confs[config_name])
							flag_marker = False
							for marker in host_specific_markers:
								taken_key = self.etcd_manager.read_key( \
									"/platform/orchestrator/marker_{}".format(marker))
								markers_dict = literal_eval(taken_key)
								if self.hostname in markers_dict:
									logger.info("{} is in the markers list and all markers will be replaced in the configs!". \
												format(self.hostname))
									match_point = "\${" + marker + "}"
									generated_cfg = re.sub(r"{}".format(match_point), \
										str(markers_dict[self.hostname]), generated_cfg)
							self.write_etcd_and_file(generated_cfg, config_name)
							logger.info("At hostname [{}] writing etcd configs [{}] and generating the new file ".format( \
																	self.hostname, config_name))
							self.reload()
						else:
							self.reload()
					except:
						logger.error("ERROR,ConfManager in {} can't update etcd for some reason !!!". \
							format(self.hostname))

					self.loaded_json['platform_state'] = new_md5_state	
		logger.clear_handler()


	@staticmethod
	def reload():

		"""
		Reloads application
		Args:
			None
		Returns:
			None
		"""
		logger = Logger(filename = "occonfman", \
				logger_name = "GwManager reload()", \
				dirname="/aux1/occonfman/logs/")
		logger.info("Restarting gw ...")
		logger.clear_handler()
		os.system("/opt/cross_plugin/cross_plugin.sh stop")
		os.system("/opt/cross_plugin/cross_plugin.sh start")
