#!/usr/bin/python3.6
import os

###custom libs
from lib.conf_manager import ConfManager



class BrowserManager(ConfManager):
	"""
	BrowserManager class
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
		self.conf_dir = "/aux0/customer/ocbrowser/etc/"
		

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


	@staticmethod
	def reload():
		"""
		Reloads application
		Args:
			None
		Returns:
			None
		"""
		os.system("ocbrowser restart")
		print("Ocbrowser is reloaded !!!")
