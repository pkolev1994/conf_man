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
sys.path.append('/aux0/customer/containers/occonfman/')
from lib.conf_manager import ConfManager
sys.path.append('/aux0/customer/containers/ocpytools/lib/')
from logger import Logger
from conf_tools import md5
from conf_tools import md5_file
from conf_tools import write_file
from conf_tools import hash_md5



class ConnManager(ConfManager):
	"""
	ConnManager class
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
		self.looking_browser = "{}_br".format(self.micro_platform)
		self.looking_gw = "{}".format(self.config_type)
		self.conf_dir = "/aux0/customer/connectors/external/"
		self.conf_dir_2 = "/aux0/customer/cross_plugin/"



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


	def get_xml_files(self):
		"""
		Get all xml files from self.conf_dir,
	 	self.conf_dir_2 and returns
		only xml filenames that consists
		self.connector_type
		Args:
			None
		Returns:
			xml_files(list)
		"""

#### for conf_dir
		connector_type = re.search(r"(.*?)\_conn", self.config_type, re.I|re.S).group(1)
		xml_files = []
		all_xml_files = [f for f in listdir(self.conf_dir) if isfile(join(self.conf_dir, f))]
		for xml in all_xml_files:
			if re.search(r"{}".format(connector_type), xml, re.I|re.S):
				xml_files.append("{}{}".format(self.conf_dir, xml))

#### for conf_dir_2
		xml_files_2 = []
		all_xml_files = [f for f in listdir(self.conf_dir_2) if isfile(join(self.conf_dir_2, f))]
		for xml in all_xml_files:
			if re.search(r"{}".format(connector_type), xml, re.I|re.S):
				# print("Type => {} XML => {}".format(connector_type, xml))
				xml_files_2.append("{}{}".format(self.conf_dir_2, xml))

		return xml_files, xml_files_2



	def check_config_status(self):
		"""
		Args:
			None
		Returns:
			None
		"""

		# xmls_1, xmls_2 = self.get_xml_files()
		# xmls = xmls_1 + xmls_2

		logger = Logger(filename = "occonfman", \
						logger_name = "ConnManager check_config_status", \
						dirname="/aux1/occonfman/logs/")

		logger.info("Checking config status ...")
		connector_type = re.search(r"^.*?\_.*?\_(.*?)\_", self.config_type, re.I|re.S).group(1)
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
			logger.info("There is a change in the configs !")
			flag = True
			ids = etcd_config["platform"][self.config_type]["general"]["ids"]
			for config_name in confs:
				taken_id = None
				if re.search(r"{}".format(connector_type), config_name, re.I|re.S):
					for id_xml in ids.keys():
						###change 09.01.2019
						if re.search(r"{}".format(config_name), id_xml, re.I|re.S):
							taken_id = ids[id_xml]
							logger.info("The id given from the web is => {}".format(taken_id))
						###change 09.01.2019
						# if re.search(r"{}\.(\d+)".format(config_name), id_xml, re.I|re.S):
						# 	taken_id = re.search(r"{}\.(\d+)". \
						# 				format(config_name), id_xml, re.I|re.S).group(1)
						# 	logger.info("The id given from the web is => {}".format(taken_id))
					flag_id = "success"
					browsers = self.get_specific_apps(self.looking_browser)
					try:
						account_id = re.search(r".*?\-(.*?)\-", config_name, re.I|re.S).group(1)
						login = re.search(r".*?\-.*?\-(.*?)\.xml", config_name, re.I|re.S).group(1)
						system_type = re.search(r"(^.*?)\-", config_name, re.I|re.S).group(1)

						host_xml = self.generate_xml_browsers_external(browsers)
						generated_external_xml = re.sub(r"(?is)<hosts>.*?<\/hosts>", \
														 "<hosts>{}</hosts>". \
													format(host_xml), confs[config_name])
						logger.info("Generating external xml => {}".format(config_name))
						######################## cross part
						cross_xml = self.generate_xml_browsers_cross(browsers,  \
																	account_id, login, system_type)
						cross_name = "{}.xml".format(login)
						generated_cross_xml = re.sub(r"(?is)<ipc>.*?<\/ipc>", "<ipc>{}</ipc>". \
														format(cross_xml), confs[cross_name])
						logger.info("Generating cross xml => {}, with account_id => {}, login => {}, system_type => {}". \
									format(config_name, account_id, login, system_type))				
						####marker logic
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
								generated_external_xml = re.sub(r"(?is){}".format(match_point), \
																str(markers_dict[self.hostname]), \
																generated_external_xml)
						####marker logic

						self.write_etcd_and_file(generated_external_xml, config_name)
						###change 09.01.2019
						#self.write_etcd_and_file(generated_cross_xml, config_name)
						self.write_etcd_and_file(generated_cross_xml, "{}.xml".format(login))
						###change 09.01.2019
						logger.info("At hostname [{}] writing etcd configs [{}] and generating the new file ".format( \
																self.hostname, config_name))
						if not self.reload(login):
							flag_id = "failed"
					######################### cross part
					except:
						flag_id = "failed"
						logger.error("ERROR,ConfManager in {} can't update etcd for some reason !!!". \
							format(self.hostname))
					self.loaded_json["md5"] = curr_md5_conf
					self.loaded_json["md5_br"] = md5(browsers)
					logger.info("Writing status in etcd /platform/statuses/{}/{}".format( \
												self.hostname, config_name))
					self.etcd_manager.write(new_key="/platform/statuses/{}/{}".format( \
													self.hostname, config_name) , \
										value= '{{"id": "{}", "timestamp": "{}", "status": "{}"}}'. \
												format(taken_id, \
														datetime.datetime.now(), \
														flag_id))			
		logger.clear_handler()


	def check_platform_status(self):

		logger = Logger(filename = "occonfman", \
						logger_name = "ConnManager check_platform_status", \
						dirname="/aux1/occonfman/logs/")
		logger.info("Checking platform status ...")

		platform_state = self.etcd_manager.get_platform_status()
		new_md5_state = hash_md5(platform_state)
		if self.loaded_json['platform_state'] != new_md5_state:
			logger.info("There is a change in the platform state!")
			browsers = self.get_specific_apps(self.looking_browser)
			if self.diff_browsers(browsers):
				connector_type = re.search(r"^.*?\_.*?\_(.*?)\_", \
											self.config_type, re.I|re.S).group(1)
				etcd_config = self.etcd_manager.get_etcd_config()
				if self.etcd_manager.CheckExistAppType(self.config_type):
					confs = etcd_config["platform"][self.config_type]["general"]["confs"]
				else:
					logger.clear_handler()
					return
				for config_name in confs:
					if re.search(r"{}".format(connector_type), config_name, re.I|re.S):
						flag_id = "success"
						try:
							account_id = re.search(r".*?\-(.*?)\-", config_name, re.I|re.S).group(1)
							login = re.search(r".*?\-.*?\-(.*?)\.xml", config_name, re.I|re.S).group(1)
							system_type = re.search(r"(^.*?)\-", config_name, re.I|re.S).group(1)

							host_xml = self.generate_xml_browsers_external(browsers)
							generated_external_xml = re.sub(r"(?is)<hosts>.*?<\/hosts>", "<hosts>{}</hosts>". \
															format(host_xml), confs[config_name])
							logger.info("Generating external xml => {}".format(config_name))
							######################## cross part
							cross_xml = self.generate_xml_browsers_cross( \
													browsers, account_id, login, system_type)
							cross_name = "{}.xml".format(login)
							generated_cross_xml = re.sub(r"(?is)<ipc>.*?<\/ipc>", "<ipc>{}</ipc>". \
															format(cross_xml), confs[cross_name])
							logger.info("Generating cross xml => {}, with account_id => {}, login => {}, system_type => {}". \
										format(config_name, account_id, login, system_type))
							####marker logic
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
									generated_external_xml = re.sub(r"(?is){}".format(match_point), \
																str(markers_dict[self.hostname]), \
																generated_external_xml)
							####marker logic
							self.write_etcd_and_file(generated_external_xml, config_name)
							self.write_etcd_and_file(generated_cross_xml, config_name)
							logger.info("At hostname [{}] writing etcd configs [{}] and generating the new file ".format( \
																	self.hostname, config_name))
							if not self.reload:
								flag_id = "failed"
						######################## cross part
						except:
							flag_id = "failed"
							logger.error("ERROR,ConfManager in {} can't update etcd for some reason !!!". \
								format(self.hostname))

						self.loaded_json['platform_state'] = new_md5_state

		logger.clear_handler()


	@staticmethod
	def reload(conn_name = None):
		"""
		Reloads application
		Args:
			None
		Returns:
			None
		"""
		logger = Logger(filename = "occonfman", \
						logger_name = "ConnManager reload()", \
						dirname="/aux1/occonfman/logs/")
		logger.info("Restarting occonectors ...")
		if conn_name:
			output = os.popen("occonnectors restart {}".format(conn_name)).read()
			logger.info("Output from connector restart of conn_name => {}".format(output))
			logger.clear_handler()
			return True
		else:
			output = os.popen("occonnectors restart").read()
			logger.info("Output from connector restart => {}".format(output))
			logger.clear_handler()
			return True
