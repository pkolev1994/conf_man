import xml.etree.ElementTree as ET
import re


from os import listdir
from os.path import isfile, join
mypath = '/home/pkolev/Git/occonfman/test/external/'

http_xml_files = []
all_xml_files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for xml in all_xml_files:
	if re.search("HTTP", xml, re.I|re.S):
		http_xml_files.append(xml)
# print(" => {}".format(http_xml_files))

for xml in http_xml_files:

	tree = ET.parse(mypath + xml)

	xmlRoot = tree.getroot()
	child = ET.Element("NewNode")
	xmlRoot.append(child)

	# tree.write("aaaaa.xml")


import xml.etree.ElementTree as et
import copy

tree = et.parse('/home/pkolev/Git/occonfman/HTTP_CLIENT-14565-HTTP_CI_LOAD_TEST.xml')
root = tree.getroot()
# root = et.parse('/home/pkolev/Git/occonfman/HTTP_CLIENT-14565-HTTP_CI_LOAD_TEST.xml').getroot()
opcdipc = root.find('opcdipc')
print(opcdipc)
hosts = root.find('opcdipc').find('hosts')
print(hosts)
host = root.find('opcdipc').find('hosts').find('host')

bks = ["book_title_1", "book_title_2", "book_title_3"]
for bk in bks:
   new_book = copy.deepcopy(host)
   new_book.find('ipaddress').text = bk
   hosts.append(new_book)

tree.write("aaaaa.xml")

print(et.tostring(root))