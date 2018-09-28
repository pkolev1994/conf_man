import copy
import json
import hashlib


def update_conf_json(json_file, key, value, state):
	"""
	Update json_file
	"""

	jsonFile = open(json_file, "r") # Open the JSON file for reading
	data = json.load(jsonFile) # Read the JSON into the buffer
	jsonFile.close() # Close the JSON file


	if state is 'add':
		if key is 'available_servers' or key is 'swarm_servers':
			data[key].append(value)
		else:
			data[key] = value
	elif state is 'remove':
		if key is 'available_servers' or key is 'swarm_servers':
			data[key].remove(value)
		else:
			data[key] = value		
	## Save our changes to JSON file

	jsonFile = open(json_file, "w+")
	jsonFile.write(json.dumps(data,  indent=4))
	jsonFile.close()



def parse_conf_json(json_file):
	"""
	Parse json_file and load it to a dictionary
	Returns:
		js_data(dict)
	"""
	try:
		with open(json_file) as json_data:
			js_data = json.load(json_data)
	except IOError:
		raise("File => {} couldn't be opened for read!".format(json_file))

	return js_data


def md5(fnames):
	"""
	Makes md5 of file_content
	Args:
		fnames(list)
	Returns:
		hash_md5.hexdigest()(str)
	"""
	hash_md5 = hashlib.md5()
	for fname in fnames:
		with open(fname, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk)
	return hash_md5.hexdigest()