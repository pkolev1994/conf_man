#!/usr/bin/python3.4
from os import listdir
from os.path import isfile
from os.path import join
import re
import os
import sys
import datetime
from ast import literal_eval
###custom libs
from lib.conf_manager import ConfManager
sys.path.append('/aux0/customer/containers/ocpytools/lib/')
from logger import Logger
from conf_tools import md5
from conf_tools import md5_file
from conf_tools import write_file
from conf_tools import hash_md5


class RestAppManager(ConfManager):
	"""
	BrowserManager class
	"""

	def __init__(self):
		"""
		Constructor
		Args:
			None
		Returns:
			None
		"""
		super().__init__()
		

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

		logger = Logger(filename = "occonfman", \
						logger_name = "RestAppManager check_config_status", \
						dirname="/aux1/occonfman/logs/")
		logger.info("Checking config status ...")

		etcd_config = self.etcd_manager.get_etcd_config()
		if self.etcd_manager.CheckExistAppType(self.config_type):
			logger.info("There is already exists {} config type in etcd".format(self.config_type))
			confs = etcd_config["platform"][self.config_type]["general"]["confs"]
		else:
			logger.clear_handler()
			return
		if not confs:
			curr_md5_conf = "Nothing"
			logger.clear_handler()
			return
		else:
			curr_md5_conf = md5(confs)

		if self.loaded_json["md5"] != curr_md5_conf:
			flag = True
			for config_name in confs:
				curr_conf_dict = literal_eval(confs[config_name])
				logger.info(confs[config_name])
				logger.info(curr_conf_dict)
				extract_dict = {config_name: curr_conf_dict['file_value']}
				md5_file_value = md5_file(["{}{}".format(curr_conf_dict['file_path'], \
														config_name)])
				if md5(extract_dict) != md5_file_value:
					write_file(filename = "{}{}".format( \
										curr_conf_dict['file_path'], \
										config_name), \
								text = curr_conf_dict['file_value'])
					flag_id = "success"
					if not self.execute_command(curr_conf_dict['command'], curr_conf_dict['regex']):
						flag_id = "failed"
					logger.info("Writing status in etcd /platform/statuses/{}/{}" \
								" and generating the new file".format(self.hostname, config_name))	

					self.write_etcd_and_file(curr_conf_dict['file_value'], \
											config_name, \
											curr_conf_dict['file_path'])
					self.etcd_manager.write(new_key="/platform/statuses/{}/{}".format( \
													self.hostname, config_name) , \
										value= '{{"id": "{}", "timestamp": "{}", "status": "{}"}}'. \
												format(curr_conf_dict['id'], \
														datetime.datetime.now(), \
														flag_id))

					self.loaded_json["md5"] = curr_md5_conf
		logger.clear_handler()




	def check_platform_status(self):
		pass


	def write_etcd_and_file(self, file_str, conf_name, conf_dir):

		logger = Logger(filename = "occonfman", \
						logger_name = "RestAppManager write_etcd_and_file", \
						dirname="/aux1/occonfman/logs/")

		logger.info("Writing value at etcd Key => /platform/{}/{}/confs/{}". \
															format(self.config_type, \
																	self.hostname, \
																	 conf_name))
		logger.clear_handler()

		self.etcd_manager.write(new_key = "/platform/{}/{}/confs/{}".format(self.config_type, \
																				self.hostname, \
																				 conf_name), \
									value= "{}".format(file_str))
		write_file(filename = "{}{}".format(conf_dir, conf_name), \
					text = file_str)


		
	@staticmethod
	def reload():
		"""
		Reloads application
		Args:
			None
		Returns:
			None
		"""
		pass


	@staticmethod
	def execute_command(command, regex):
		"""
		Reloads application
		Args:
			None
		Returns:
			None
		"""
		logger = Logger(filename = "occonfman", \
				logger_name = "RestAppManager execute_command()", \
				dirname="/aux1/occonfman/logs/")
		logger.info("Executing RestAppManager {}...".format(command))
		logger.clear_handler()
		output = os.popen("{}".format(command)).read()
		if re.search(r"{}".format(regex), output, re.I|re.S):
			return True
		else:
			return False
		#os.system(command)
