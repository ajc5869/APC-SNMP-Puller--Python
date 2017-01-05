#Contains the funtions for app.py (the main web app)
#Author: Andrew Cozzetta

import os
import subprocess
import re
from pathlib import Path
import datetime


CONST_COMMUNITY_STRING = "public"


def write_date(ip_address, query_id):
	file = open("outputs/" + query_id + ".html", 'a')
	file.write('<p>-</p>')
	file.write("<p><u><b>Last Query:</u></b> " + str(datetime.datetime.now()) + "</p>")
	file.close()


def get_apc_name(ip_address, query_id):
	try:
		for APCName in re.compile('"[^"]*"').findall(str(subprocess.check_output("snmpget -v1 -Cf -c " + CONST_COMMUNITY_STRING + " " + ip_address + " sPDUMasterConfigPDUName.0",shell=True))):
			APCName = APCName[1:-1]
			file = open("outputs/" + query_id + ".html", 'a')
			file.write("<u><b>Name:</u></b> " + APCName + '<span style="margin-left:1em">')
			file.close()
	except subprocess.CalledProcessError as e:
		file = open("outputs/" + query_id + ".html", 'a')
		file.write('<b><font color="red">Error: Could not retrieve SNMP data</font></b>')
		file.write('<p>-</p>')
		file.close()
		return "Error"


def get_apc_model(ip_address, query_id):
	try:
		for APCModel in re.compile('"[^"]*"').findall(str(subprocess.check_output("snmpget -v1 -Cf -c " + CONST_COMMUNITY_STRING + " " + ip_address + " sPDUIdentModelNumber.0",shell=True))):
			APCModel = APCModel[1:-1]
			file = open("outputs/" + query_id + ".html",'a')
			file.write("<u><b>Model:</u></b> " + APCModel)
			file.close()
	except subprocess.CalledProcessError as e:
		return "Error"


def get_apc_serial(ip_address, query_id):
	try:
		for APCSerial in re.compile('"[^"]*"').findall(str(subprocess.check_output("snmpget -v1 -Cf -c " + CONST_COMMUNITY_STRING + " " + ip_address + " sPDUIdentSerialNumber.0",shell=True))):
			APCSerial = APCSerial[1:-1]
			return_val = "<u><b>Serial:</u></b> " + APCSerial
			file = open("outputs/" + query_id + ".html",'a')
			file.write("<p>" + return_val + "</p>")
			file.close()
	except subprocess.CalledProcessError as e:
		return "Error"


def write_ip(ip_address, query_id):
	file = open("outputs/" + query_id + ".html",'a')
	file.write("<u><b>IP:</u></b> " + ip_address + '<span style="margin-left:1em">')
	file.close()


def get_num_outlets(ip_address, query_id):
	try:
		num_outlets = str(subprocess.check_output("snmpget -v1 -Cf -c " + CONST_COMMUNITY_STRING + " " + ip_address + " rPDUIdentDeviceNumOutlets.0",shell=True))
		num_outlets = num_outlets.split("INTEGER: ",1)
		num_outlets = num_outlets[1]
		return(int(num_outlets))
	except subprocess.CalledProcessError as e:
		return "Error"


def get_num_banks(ip_address, query_id):
	try:
		num_banks = str(subprocess.check_output("snmpget -v1 -Cf -c " + CONST_COMMUNITY_STRING + " " + ip_address + " rPDUStatusBankTableSize.0",shell=True))
		num_banks = num_banks.split("INTEGER: ",1)
		num_banks = num_banks[1]

		return(int(num_banks))

	except subprocess.CalledProcessError as e:
		return "Error"


def get_bank_load(ip_address, query_id):
	try:
		bank_size = get_num_banks(ip_address, query_id)
		max_bank_index = 0

		if bank_size == 0:
			max_bank_index = 1

		if bank_size >= 2:
			max_bank_index = bank_size + 1

		starting_bank_index = 1
		while starting_bank_index <= max_bank_index:
			TotalLoad = str(subprocess.check_output("snmpget -v1 -Cf -c " + CONST_COMMUNITY_STRING + " " + ip_address + " rPDULoadStatusLoad." + str(starting_bank_index),shell=True))
			TotalLoad = TotalLoad[46:]

			if starting_bank_index == 1:
				file = open("outputs/" + query_id + ".html",'a')
				file.write('<p></p><u><b>Total Bank Load:</u></b> ' + str(float(TotalLoad)/10) + " amps" + '<span style="margin-left:1em">')
				file.close()

			else:
				file = open("outputs/" + query_id + ".html",'a')
				file.write("<u><b>Bank " + str(starting_bank_index-1) + " Load:</u></b> " + str(float(TotalLoad)/10) + " amps" + '<span style="margin-left:1em">')
				file.close()
			starting_bank_index += 1
	except subprocess.CalledProcessError as e:
		return "Error"


def get_outlet_status(ip_address, query_id):
	on_outlets = []
	off_outlets = []

	try:
		file = open("outputs/" + query_id + ".html",'a')
		file.write("<p></p>")
		file.write("<u><b>Outlet Status:</u></b> ")
		file.close()

		outlet_index = 1
		num_to_newline = 0
		while outlet_index <= get_num_outlets(ip_address, query_id):
			outlet_status = str(subprocess.check_output("snmpget -v1 -Cf -c " + CONST_COMMUNITY_STRING + " " + ip_address + " rPDUOutletStatusOutletState." + str(outlet_index),shell=True))
			status_on = "outletStatusOn"
			status_off = "outletStatusOff"

			if status_on in outlet_status:
				on_outlets.append(str(outlet_index))

			if status_off in outlet_status:
				off_outlets.append(str(outlet_index))

			outlet_index += 1
			num_to_newline += 1

		on_outlets_string = ", ".join(on_outlets)
		off_outlets_string = ", ".join(off_outlets)
		
		file = open("outputs/" + query_id + ".html",'a')
		file.write('<font color="limegreen">On</font> Outlets: [' + on_outlets_string + ']')
		file.write('<span style="margin-left:1em"><font color="red">Off</font> Outlets: [' + off_outlets_string + ']</span><br>')
		file.write('<p>-</p>')
		file.close()
		
	except subprocess.CalledProcessError as e:
		return "Error"


def ip_extractor(ip_range, octet_list):
	split_ip = ip_range.split("-")
	
	first_octet = split_ip[0].split(".")[0]
	second_octet = split_ip[0].split(".")[1]
	third_octet = split_ip[0].split(".")[2]
	fourth_octet = split_ip[0].split(".")[3]
	right_side = split_ip[1]
	
	octet_list.extend([int(first_octet), int(second_octet), int(third_octet), int(fourth_octet), int(right_side)])

	return octet_list