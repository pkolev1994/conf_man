#!/usr/bin/python3.4
from os import listdir
from os.path import isfile, join
from ast import literal_eval
import re
import copy
import json
import os
import socket
import datetime
import sys
###custom libs

sys.path.append('/aux0/customer/containers/ocpytools/lib/')
from logger import Logger
from etcd_client import EtcdManagement
from conf_tools import *


class ConfManager():

	def __init__(self, local_configs = None):
		"""
		Parent class constructor
		Args:
			None
		Returns:
			None
		"""
		self.loaded_json = {"md5": "", "platform_state": "", "md5_gw": "",\
							 "md5_br": "", "md5_nodes_xml": ""}
		self.etcd_manager = EtcdManagement()
		self.local_configs = local_configs
		self.hostname = socket.gethostname()
		self.micro_platform = re.search(r'(.*?)\_', self.hostname, re.I|re.S).group(1)
		self.config_type = re.search(r'(.*?)\_\d+', self.hostname, re.I|re.S).group(1)
		if self.local_configs:
			if not self.etcd_manager.CheckExistAppType(self.config_type):
				for confpath in self.local_configs.split(","):
					file_value = ReadFile(confpath)
					key_name = os.path.split(confpath)[1]
					self.etcd_manager.write("/platform/{}/general/confs/{}".format(self.config_type, key_name) ,file_value)

#####
			self.initializing_etcd_config()
			etcd_config = self.etcd_manager.get_etcd_config()
			confs = etcd_config["platform"][self.config_type]["general"]["confs"]
			self.loaded_json['md5'] = md5(confs)


	def initializing_etcd_config(self):
		"""
		Initializing etcd configs in 
		the etcd config tree of the 
		new container app
		Args:
			None
		Returns:
			None
		"""
		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager initializing_etcd_config", \
						dirname="/aux1/occonfman/logs/")

		etcd_config = self.etcd_manager.get_etcd_config()
		confs = etcd_config["platform"][self.config_type]["general"]["confs"]
		logger.info("Initializing etcd configs in the etcd config tree of {}".format(self.hostname))
		for config_name in confs.keys():
			self.etcd_manager.write \
				(new_key = "/platform/{}/{}/confs/{}".format( \
				self.config_type, \
				self.hostname, \
				config_name), \
				value = confs[config_name])
		logger.clear_handler()


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
		self.etcd_manager.write( \
			new_key = "/platform/{}/{}/confs/{}". \
						format(self.config_type, self.hostname, filename), \
			value= file_string)


	def check_config_status(self):
		"""
		Getting all filenames in the self.conf_dir
		If in self.loaded_json["md5"] is different
		from md5 of configs in etcd then
		iterating through each conf from etcd and 
		diff them with the local files,
		when there is a difference the function
		make new file with the conf from etcd in
		self.conf_dir and writes in /platform/statuses/
		key with the filename and value json string=>
		{id: int, 
		 timestamp: time
		 status: str
		 }
		Cals reload if it is success
		Args:
			None
		Returns:
			None
		"""

##### old
		# logger = Logger(filename = "occonfman", \
		# 				logger_name = "ConfManager check_config_status", \
		# 				dirname="/aux1/occonfman/logs/")
		# logger.info("Checking config_status ...")
		# xmls = [f for f in listdir(self.conf_dir) if isfile(join(self.conf_dir, f))]
		# etcd_config = self.etcd_manager.get_etcd_config()
		# confs = etcd_config["platform"][self.config_type]["general"]["confs"]
		# if not confs:
		# 	curr_md5_conf = "Nothing"
		# else:
		# 	curr_md5_conf = md5(confs)
##### old
################################new way
		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager check_config_status", \
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
################################new way
		if self.loaded_json["md5"] != curr_md5_conf:
			flag = True
			ids = etcd_config["platform"][self.config_type]["general"]["ids"]
			try:
				# if not xmls:
				# 	for config_name in confs:
				# 		taken_id = None
				# 		for id_xml in ids.keys():
				# 			if re.search(r"{}\.(\d+)".format(config_name), id_xml, re.I|re.S):
				# 				taken_id = re.search(r"{}\.(\d+)". \
				# 							format(config_name), id_xml, re.I|re.S).group(1)
				# 		flag_id = "success"
				# 		try:
				# 			write_file(filename = "{}{}".format(self.conf_dir_2, config_name), \
				# 							text = confs[config_name])
				# 		except:
				# 			flag_id = "failed"
				# 		self.etcd_file_updating(file_string=confs[config_name], \
				# 								filename = config_name)
				# 		self.etcd_manager.write(new_key="/platform/statuses/{}/{}".format( \
				# 										self.hostname, config_name) , \
				# 							value= "{{id: {}, timestamp: {}, status: {}}}". \
				# 									format(taken_id, \
				# 											datetime.datetime.now(), \
				# 											flag_id))
				# else:
				for config_name in confs:
					taken_id = None
					for id_xml in ids.keys():
						###change 09.01.2019
						if re.search(r"{}".format(config_name), id_xml, re.I|re.S):
							taken_id = ids[id_xml]
							logger.info("The id given from the web is => {}".format(taken_id))
						###change 09.01.2019
					flag_id = "success"
					try:
						extract_dict = {config_name: confs[config_name]}
						if md5(extract_dict) != md5_file(["{}{}".format(self.conf_dir_2, config_name)]):
							write_file(filename = "{}{}".format(self.conf_dir_2, config_name), \
											text = confs[config_name])
					except:
						flag_id = "failed"
					logger.info("Writing status in etcd /platform/statuses/{}/{} and generating the new file".format( \
												self.hostname, config_name))
					self.write_etcd_and_file(confs[config_name], config_name)
					self.etcd_manager.write(new_key="/platform/statuses/{}/{}".format( \
													self.hostname, config_name) , \
										value= '{{"id": "{}", "timestamp": "{}", "status": "{}"}}'. \
												format(taken_id, \
														datetime.datetime.now(), \
														flag_id))
			except:
				flag = False
				logger.error("ERROR,ConfManager in {} can't update etcd for some reason !!!". \
						format(self.hostname))
			if flag:
				self.loaded_json["md5"] = curr_md5_conf
				self.reload()

		logger.clear_handler()



	def get_specific_apps(self, app):
		"""
		get specific microplatform app
		Args:
			app(str)
		Returns:
			app_containers(dict)
		"""


		apps = literal_eval(self.etcd_manager.get_platform_status())
		app_containers = {}
		for host in apps.keys():
			if app in apps[host]:
				app_containers.update(apps[host][app])
		return app_containers



	def diff_browsers(self, br_containers):		

		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager diff_browsers", \
						dirname="/aux1/occonfman/logs/")

		if md5(br_containers) != self.loaded_json["md5_br"]:
			self.loaded_json["md5_br"] = md5(br_containers)
			logger.info("There is a different browser state in the platform now!")
			logger.clear_handler()
			return True
		else:
			logger.info("No change in browser state of the platform!")
			logger.clear_handler()
			return False



	def diff_gws(self, gw_containers):		

		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager diff_gws", \
						dirname="/aux1/occonfman/logs/")

		if md5(br_containers) != self.loaded_json["md5_gw"]:
			self.loaded_json["md5_gw"] = md5(br_containers)
			logger.info("There is a different gws state in the platform now!")
			logger.clear_handler()
			return True
		else:
			logger.info("No change in gws state of the platform!")
			logger.clear_handler()
			return False


	def generate_xml_browsers_external(self, br_containers):

		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager generate_xml_browsers_external", \
						dirname="/aux1/occonfman/logs/")
		xml = ""
		for br in br_containers:
			xml += """<host>
			        <ipaddress>{}</ipaddress>
			        <port>5049</port>
			      </host>\n""".format(br)

		logger.info("Generating external browsers config section")
		logger.clear_handler()
		return xml


	def generate_xml_browsers_cross(self, br_containers, account_id, login, system_type):

		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager generate_xml_browsers_cross", \
						dirname="/aux1/occonfman/logs/")

		xml = ""
		for br in br_containers:
			xml += """<connection>
				          <enabled>Y</enabled>
				          <type>client</type>
				          <account_id>{}</account_id>
				          <ip>{}</ip>
				          <port>5049</port>
				          <login>{}</login>
				          <password>{}</password>
				          <system_type>{}</system_type>
				     </connection>\n""".format(account_id, \
				     							br, \
				     							login, \
				     							account_id,
				     							system_type)
		logger.info("Generating cross browsers config section")
		logger.clear_handler()
		return xml


	def generate_cfg_cross_plugin(self, br_containers, account_id, login, system_type):

		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager generate_cfg_cross_plugin", \
						dirname="/aux1/occonfman/logs/")

		xml = ""
		for br in br_containers:
			xml += """<connection>
				          <enabled>Y</enabled>
				          <type>client</type>
				          <account_id>{}</account_id>
				          <ip>{}</ip>
				          <port>5049</port>
				          <login>{}</login>
				          <password>{}</password>
				          <system_type>{}</system_type>
				     </connection>\n""".format(account_id, \
				     							br, \
				     							login, \
				     							account_id,
				     							system_type)

		logger.info("Generating cfg cross_plugin config section")
		logger.clear_handler()
		return xml



	def write_etcd_and_file(self, file_str, conf_name):

		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager write_etcd_and_file", \
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
		write_file(filename = "{}{}".format(self.conf_dir, conf_name), \
					text = file_str)


	def check_nodes_xml(self):
		"""
		Looks and generates new nodes.xml
		in the container if there is a 
		change in etcd_key /platform/orchestrator/nodes_xml
		Args:
			None
		Returns:
			None
		"""
		logger = Logger(filename = "occonfman", \
						logger_name = "ConfManager check_nodes_xml", \
						dirname="/aux1/occonfman/logs/")

		nodes_xml = self.etcd_manager.read_key("/platform/orchestrator/nodes_xml")
		new_md5_nodes_xml = hash_md5(nodes_xml)
		if self.loaded_json['md5_nodes_xml'] != new_md5_nodes_xml:
			logger.info("There is a change in nodes.xml!")
			write_file(filename = "/aux0/customer/platform/nodes.xml", text = nodes_xml)	
<<<<<<< HEAD
=======
			self.loaded_json["md5_nodes_xml"] = new_md5_nodes_xml
>>>>>>> origin/T103171
