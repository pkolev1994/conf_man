import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
import re
import copy
import json
import os
import socket
###custom libs
from lib.etcd_client import EtcdManagement
from lib.conf_tools import update_conf_json
from lib.conf_tools import parse_conf_json
from lib.conf_tools import md5




class ConnManager():

	def __init__(self):
		"""
		Constructor
		Args:
			None
		Returns:
			None
		"""
		self.conf_dir = "/aux0/customer/connectors/external/"
		self.conf_dir_2 = "/aux0/customer/cross_plugin/"
		self.conf_manager_file = "/home/pkolev/Containers/conf_manager/conf_manager.json"
		# self.connector_type= re.search(r'(.*?)\_conn', socket.gethostname(), re.I|re.S).group(1)
	#####for testing on host to show that works 
		self.connector_type= re.search(r'(.*?$)', socket.gethostname(), re.I|re.S).group(1)
		if self.connector_type == 'g3':
			self.connector_type = "smpp"
	#####for testing on host to show that works 


		# self.conf_dir = "/home/pkolev/Git/occonfman/test/test_external/"
		# self.conf_manager_file = "http_conn_manager.json"

	def get_new_browsers(self, platform_status):
		"""
		Parse the platform status from etcd
		and compare it according the connector file
		Args:
			platform_status(dict)
		Returns:
			new_browsers(dict)
		"""
		loaded_json = parse_conf_json(self.conf_manager_file)
		new_browsers = {}
		for host in platform_status.keys():
			for application in platform_status[host]:
				# print("App => {}".format(application))
				if application == 'br':
					for container_name in platform_status[host][application]:
						if container_name not in loaded_json:
							new_browsers[container_name] = platform_status[host][application][container_name]
		return new_browsers


	def remove_browsers(self, platform_status):
		"""
		Parse the platform status from etcd
		and compare it according the connector file
		Args:
			platform_status(dict)
		Returns:
			new_browsers(dict)
		"""
		loaded_json = parse_conf_json(self.conf_manager_file)
		new_browsers = {}

		for container_name in loaded_json.keys():
			flag = False
			for host in platform_status.keys():
				if container_name in platform_status[host]['br']:
					flag = True
			if not flag:
				new_browsers[container_name] = loaded_json[container_name]

		return new_browsers



	def get_new_ussd_gws(self, platform_status):
		"""
		Parse the platform status from etcd
		and compare it according the connector file
		Args:
			platform_status(dict)
		Returns:
			ussd_gws(dict)
		"""
		loaded_json = parse_conf_json(self.conf_manager_file)
		ussd_gws = {}
		for host in platform_status.keys():
			for application in platform_status[host]:
				# print("App => {}".format(application))
				# if application == 'ussd_gw':
				if application == 'ipgw':
					for container_name in platform_status[host][application]:
						if container_name not in loaded_json:
							ussd_gws[container_name] = platform_status[host][application][container_name]
		return ussd_gws


	def remove_ussd_gws(self, platform_status):
		"""
		Parse the platform status from etcd
		and compare it according the connector file
		Args:
			platform_status(dict)
		Returns:
			ussd_gws(dict)
		"""
		loaded_json = parse_conf_json(self.conf_manager_file)
		ussd_gws = {}
		
		for container_name in loaded_json.keys():
			flag = False
			for host in platform_status.keys():
				# if container_name in platform_status[host]['ussd_gw']:
				if container_name in platform_status[host]['ipgw']:
					flag = True
			if not flag:
				ussd_gws[container_name] = loaded_json[container_name]

		return ussd_gws


	def get_xml_files(self):
		"""
		Get all xml files and returns
		only xml filenames that consist 'http'
		Args:
			None
		Returns:
			xml_files(list)
		"""
		xml_files = []
		all_xml_files = [f for f in listdir(self.conf_dir) if isfile(join(self.conf_dir, f))]
		for xml in all_xml_files:
			if re.search(r"{}".format(self.connector_type), xml, re.I|re.S):
				xml_files.append("{}{}".format(self.conf_dir, xml))

#### for conf_dir_2
		xml_files_2 = []
		all_xml_files = [f for f in listdir(self.conf_dir_2) if isfile(join(self.conf_dir_2, f))]
		for xml in all_xml_files:
			if re.search(r"{}".format(self.connector_type), xml, re.I|re.S):
				# print("Type => {} XML => {}".format(self.connector_type, xml))
				xml_files_2.append("{}{}".format(self.conf_dir_2, xml))

		return xml_files, xml_files_2


	def update_configs(self, browsers = None, ussd_gws = None):
		"""
		Added browsers in http connector
		config
		Args:
			browsers(dict)
		Returns:
			None
		"""
		xml_files, xml_files_2 = self.get_xml_files()

		# print("XML FILES => {}".format(xml_files))
		# print("XML FILES 2 => {}".format(xml_files_2))
		# # print("Browsers => {}".format(browsers))
		# print("USSDGW => {}".format(ussd_gws))
		if browsers:
			for xml in xml_files:
				try:
					tree = ET.parse(xml)
					root = tree.getroot()
					for hostname in browsers.keys():
						hosts = root.find('opcdipc').find('hosts')
						host = root.find('opcdipc').find('hosts').find('host')
						new_host = copy.deepcopy(host)
						new_host.find('ipaddress').text = browsers[hostname]
						hosts.append(new_host)
						update_conf_json(json_file = self.conf_manager_file, \
										state= 'add', \
										key= hostname, \
										value=browsers[hostname])
						tree.write(xml)
				except:
					print("ERROR, {} file can't be updated for some reason".format(xml))

			for xml in xml_files_2:
				try:
					tree = ET.parse(xml)
					root = tree.getroot()
					for hostname in browsers.keys():
						ipc = root.find('connection_ccb').find('config').find('ipc')
						connection = root.find('connection_ccb').find('config').find('ipc').find('connection')
						new_connection = copy.deepcopy(connection)
						new_connection.find('ip').text = browsers[hostname]
						ipc.append(new_host)
						update_conf_json(json_file = self.conf_manager_file, \
										state= 'add', \
										key= hostname, \
										value=browsers[hostname])
						tree.write(xml)
				except:
					print("ERROR, {} file can't be updated for some reason".format(xml))


		if ussd_gws:
			for xml in xml_files:
				increment_id = 0
				try:
					tree = ET.parse(xml)
					root = tree.getroot()
					for hostname in ussd_gws.keys():
						conn_type = root.find('protocolspecific'). \
									find('subconnectors'). \
									find('subconnector'). \
									find('commonparams'). \
									find('ConnType').text
						if conn_type == '2':
							smpp_clients = root.find('protocolspecific'). \
								find('subconnectors'). \
								find('subconnector'). \
								find('SMPPClients')
							smpp_client = root.find('protocolspecific'). \
								find('subconnectors'). \
								find('subconnector'). \
								find('SMPPClients'). \
								find('SMPPClient')

							all_smpp = root.find('protocolspecific'). \
								find('subconnectors'). \
								find('subconnector'). \
								find('SMPPClients'). \
								findall('SMPPClient')
							id_ll = []
							for client in all_smpp:
								# print("Client => {}".format(client))
								id_ll.append(int(client.find('id').text))
							max_id = max(id_ll) + 1
							# print("MAx id => {}".format(max_id))
							new_smpp_client = copy.deepcopy(smpp_client)
							new_smpp_client.find('IP').text = ussd_gws[hostname]
							new_smpp_client.find('id').text = str(max_id) 
							smpp_clients.append(new_smpp_client)
							# print("After append")
							update_conf_json(json_file = self.conf_manager_file, \
											state= 'add', \
											key= hostname, \
											value=ussd_gws[hostname])
							tree.write(xml)
				except:
					print("ERROR, {} file can't be updated for some reason".format(xml))

	def check_config_status(self):
		"""
		Makes md5 of curr config and 
		and diff it with the  md5 from
		self.conf_manager_file
		Args:
			None
		Returns:
			None
		"""
		xmls_1, xmls_2 = self.get_xml_files()
		xmls = xmls_1 + xmls_2
		loaded_md5_conf = parse_conf_json(self.conf_manager_file)["md5"]
		curr_md5_conf = md5(xmls)
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
		os.system("occonnectors restart")