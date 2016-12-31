#Purpose: Pull SNMP info from APC devices
#Author: Andrew Cozzetta

from flask import Flask, render_template
import os
from pathlib import Path
import uuid
import GrabNParseFuncs

app = Flask(__name__)

CONST_SERVER_IP = "0.0.0.0"
CONST_PORT_NUMBER = 80
CONST_COMMUNITY_STRING = "public"


def main(ip_address, query_id):
	#GrabNParseFuncs.write_date(ip_address, query_id)
	GrabNParseFuncs.write_ip(ip_address, query_id)
	if GrabNParseFuncs.get_apc_name(ip_address, query_id) == "Error":
		return
	GrabNParseFuncs.get_apc_model(ip_address, query_id)
	#GrabNParseFuncs.get_apc_serial(ip_address, query_id)
	GrabNParseFuncs.get_bank_load(ip_address, query_id)
	GrabNParseFuncs.get_outlet_status(ip_address, query_id)


@app.route("/")
def test():
	return render_template("index.html", ip_address=CONST_SERVER_IP)


@app.route("/dev/<ip_address>", methods=['GET'])
def run_me(ip_address):
	query_id = str(uuid.uuid1())
	Path("outputs/" + query_id + ".html").touch()

	if len(ip_address) > 15 or len(ip_address) < 7:
		return render_template("invalid_ip_range.html")

	main(ip_address, query_id)
	final_out = open("outputs/" + query_id + ".html", 'r').read()
	return final_out
	final_out.close()

@app.route("/range/<ip_range>")
def ip_range(ip_range):
	octet_list = []
	try:
		GrabNParseFuncs.ip_extractor(ip_range, octet_list)
	except:
		return render_template("invalid_ip_range.html")
	first_octet = octet_list[0]
	second_octet = octet_list[1]
	third_octet = octet_list[2]
	fourth_octet = octet_list[3]
	last_ip = octet_list[4]

	if last_ip >= 255 or last_ip <= 0:
		return render_template("invalid_ip_range.html")

	if fourth_octet > last_ip:
		return render_template("invalid_ip_range.html")

	query_id = str(uuid.uuid1())
	Path("outputs/" + query_id + ".html").touch()

	file = open("outputs/" + query_id + ".html", 'a')

	file.write("<p><u><b>Requested IP Range:</u></b> " + str(first_octet) + "." + str(second_octet) + "." + str(third_octet) + "." + str(fourth_octet) + "-" + str(last_ip) + "</p>")
	file.write("<p>-</p>")
	file.close()

	while fourth_octet <= last_ip:
		main(str(first_octet) + "." + str(second_octet) + "." + str(third_octet) + "." + str(fourth_octet), query_id)
		
		fourth_octet += 1
	final_out = open("outputs/" + query_id + ".html", 'r').read()
	return final_out
	final_out.close()


if __name__ == "__main__":
    app.run(host=CONST_SERVER_IP, port=CONST_PORT_NUMBER, threaded=True, debug=True)