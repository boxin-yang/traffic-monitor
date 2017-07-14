import requests
import subprocess
import time

background_ip_list = []
SERVER_URL =  "http://crowdedmah.herokuapp.com/updateWifi"

def upload_data(device_count):
	crowdedness = 0
	if (device_count < 20):
		crowdedness = 1
	elif (device_count < 35):
		crowdedness = 2
	elif (device_count < 55):
		crowdedness = 3
	elif (device_count < 75):
		crowdedness = 4
	else:
		crowdedness = 5

	turn_off_wifi_cmd = "networksetup -setairportpower en0 off"
	turn_on_wifi_cmd = "networksetup -setairportpower en0 on"

	print("Turn off the wifi")
	subprocess.Popen(turn_off_wifi_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
	time.sleep(5)

	print("Turn on the wifi")
	subprocess.Popen(turn_on_wifi_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
	time.sleep(5)

	payload = {'mags': int(crowdedness)}
	CrowdedMah_POST = requests.post(SERVER_URL, data=payload)
	print("Posting to", SERVER_URL, "with scale", crowdedness)
	print("Code returned from server is", CrowdedMah_POST)

def parse_stream_line(stream_line):
	if not stream_line:
		return "empty"

	return stream_line.strip().split()[2]

def collect_background_ip():
	print("Collecting background noise now. The process will run for 100 seconds.")

	tshark_cmd = "tshark -i en0 -I -Y \"wlan.fc.type_subtype eq 4\" -a duration:100"

	packets_stream = subprocess.Popen(tshark_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()

	packets_stream_lines = packets_stream.strip().split("\n")

	ip_count = {}

	for packet_stream_line in packets_stream_lines:
		sender_ip = parse_stream_line(packet_stream_line)
		if (sender_ip == "empty"):
			break

		if sender_ip not in ip_count:
			ip_count[sender_ip] = 1
		else :
			ip_count[sender_ip] += 1

	for ip, count in ip_count.iteritems():
		# print("ip",ip, "has count", count)
		if(count >= 10):
			print("adding", ip, "int the background ip list")
			background_ip_list.append(ip)

def spy():
	print("Running controller in monitor mode for 200 seconds to capture probe request")
	tshark_cmd = "tshark -i en0 -I -Y \"wlan.fc.type_subtype eq 4\" -a duration:200"
	
	packets_stream = subprocess.Popen(tshark_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
	
	packets_stream_lines = packets_stream.strip().split("\n")

	unique_ip_list = []

	for packet_stream_line in packets_stream_lines:
		sender_ip = parse_stream_line(packet_stream_line)
		if (sender_ip == "empty"):
			break
		if (sender_ip not in unique_ip_list) and (sender_ip not in background_ip_list):
			unique_ip_list.append(sender_ip)

	print("Monitoring finished.\nThere are", len(unique_ip_list)," unique ip sending probe request:")
	print(unique_ip_list)
	# upload_data(len(unique_ip_list))

# collect_background_ip()
print ""
while(True):
	spy()