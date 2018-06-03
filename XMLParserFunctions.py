# MODULE FOR FUNCTIONS

import xml.etree.ElementTree as ET
import requests
import sys
import hashlib
import json
import time

# this is is an EXAMPLE function that can be used to schedule the Parser to refresh at intervals. Takes the XMLFeedParser function and the interval as parameters.
def intervalScheduler(function, interval):
    # configure interval to refresh the XMLFeedParser (in seconds, 3600s = 1h, 86400s = 1d)
    setInterval = interval
    XMLFeedParser = function

    # user feedback
    sys.stdout.write("\n")
    sys.stdout.write("XML Feed Parser will be refreshed every %d seconds. Please use ctrl-C to exit.\n" %interval)
    sys.stdout.write("\n")

    # interval loop, unless keyboard interrupt
    try:
        while True:
            XMLFeedParser()
            sys.stdout.write("\n")
            sys.stdout.write("IntervalScheduler executed, current interval is %d seconds!\n" %interval)
            sys.stdout.write("\n")
            time.sleep(setInterval)
    # handle keyboard interrupt
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write("Exiting... XML Feed Parser will not be automatically refreshed anymore.\n")
        sys.stdout.write("\n")
        sys.stdout.flush()
        pass

# this function calculates the MD5 hash of a file. this can be used to calculate the MD5 of the previous XML file with the new one. 
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Function to make API calls to FMC
def APIcaller(object_id, objectgroup_name, object_type, objectgroup_type, put_list, object_field):
	# Disable warnings regarding Certs, please use certs in production
	requests.packages.urllib3.disable_warnings()

	# input FMC IP
	server = "https://10.10.10.72"

	# input FMC username
	username = "admin"
	if len(sys.argv) > 1:
		username = sys.argv[1]

	# input FMC password
	password = "Cisco123"
	if len(sys.argv) > 2:
		password = sys.argv[2]

	r = None
	headers = {'Content-Type': 'application/json'}
	api_auth_path = "/api/fmc_platform/v1/auth/generatetoken"
	auth_url = server + api_auth_path
	try:
		######### !IMPORTANT! 2 ways of making a REST call are provided: !IMPORTANT! #########
		# One with "SSL verification turned off" and the other with "SSL verification turned on".
		# The one with "SSL verification turned off" is uncommented. If you like to use the other then
		# uncomment the line where "verify='/path/to/ssl_certificate'"" and comment the line with "verify=False" (this is recommended!)
		
		# REST call with SSL verification turned off:
		r = requests.post(auth_url, headers=headers, auth=requests.auth.HTTPBasicAuth(username,password), verify=False)
		
		# REST call with SSL verification turned on: Download SSL certificates from your FMC first and provide its path for verification.
		#r = requests.post(auth_url, headers=headers, auth=requests.auth.HTTPBasicAuth(username,password), verify='/path/to/ssl_certificate')
		
		# create rest of headers
		auth_headers = r.headers
		auth_token = auth_headers.get('X-auth-access-token', default=None)
		if auth_token == None:
			print("auth_token not found. Exiting...")
			sys.exit()
	except Exception as err:
		print ("Error in generating auth token --> "+str(err))
		sys.exit()

	headers['X-auth-access-token']=auth_token

	# Define API path 
	api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/" + objectgroup_type + "s/" + object_id
	#api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/networkgroups/" + object_id
	#api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/networkgroups/000C2943-1B9D-0ed3-0000-025769805120"    
	url = server + api_path
	if (url[-1] == '/'):
	    url = url[:-1]
	 

	# create empty dictionary and list, to form JSON later
	object_dict = {}
	group_list = []

	# loop through list and put in right format for API call, all fields come from function call
	for element in put_list:
		object_dict["type"] = object_type
		object_dict[object_field] = element # VALUE
		group_list.append(object_dict.copy())

	put_data = {}

	# add extra fields to JSON
	put_data["id"] = object_id
	put_data["name"] = objectgroup_name
	put_data["type"] = objectgroup_type
	put_data["literals"] = group_list

	try:
	    # REST call with SSL verification turned off (NOT RECOMMENDED, TESTING ONLY)
	    r = requests.put(url, data=json.dumps(put_data), headers=headers, verify=False)
	    # REST call with SSL verification turned on (RECOMMENDED FOR PRODUCTION)
	    #r = requests.put(url, data=json.dumps(put_data), headers=headers, verify='/path/to/ssl_certificate')
	    status_code = r.status_code
	    resp = r.text
	    if (status_code == 200):
	        print("Put was successful...")
	        json_resp = json.loads(resp)
	        print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
	    else:
	        r.raise_for_status()
	        print("Status code:-->"+status_code)
	        print("Error occurred in PUT --> "+resp)
	except requests.exceptions.HTTPError as err:
	    print ("Error in connection --> "+str(err))
	finally:
	    if r: r.close()

	try:
	    # REST call with SSL verification turned off (NOT RECOMMENDED, TESTING ONLY)
	    r = requests.put(url, data=json.dumps(put_data), headers=headers, verify=False)
	    # REST call with SSL verification turned on (RECOMMENDED FOR PRODUCTION)
	    #r = requests.put(url, data=json.dumps(put_data), headers=headers, verify='/path/to/ssl_certificate')
	    status_code = r.status_code
	    resp = r.text
	    if (status_code == 200):
	        print("Put was successful, output below:")
	        json_resp = json.loads(resp)
	        print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
	    else:
	        r.raise_for_status()
	        print("Status code:-->"+status_code)
	        print("Error occurred in PUT --> "+resp)
	except requests.exceptions.HTTPError as err:
	    print ("Error in connection --> "+str(err))
	finally:
	    if r: r.close()
 

