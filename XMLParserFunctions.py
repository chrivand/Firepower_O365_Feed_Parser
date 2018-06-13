# MODULE FOR SUPPORTING FUNCTIONS FOR XMLParserMainScript

# Copyright (c) 2018 Cisco and/or its affiliates.
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.0 (the "License"). You may obtain a copy of the
# License at
#                https://developer.cisco.com/docs/licenses
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

# import libraries
import xml.etree.ElementTree as ET
import requests
import sys
import hashlib
import json
import time
import datetime

# Function that can be used to schedule the XMLParser to refresh at intervals. Caution: this creates an infinite loop.
# Takes the XMLFeedParser function and the interval as parameters. 
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
        	# get current time, for user feedback
        	date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        	sys.stdout.write("\n")
        	sys.stdout.write("[%s] XMLFeedParser executed by IntervalScheduler, current interval is %d seconds. Please use ctrl-C to exit.\n" % (date_time, interval))
        	sys.stdout.write("\n")
        	# sleep for X amount of seconds and then run again. Caution: this creates an infinite loop to check the XML file for changes
        	time.sleep(setInterval)

    # handle keyboard interrupt
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write("Exiting... XML Feed Parser will not be automatically refreshed anymore.\n")
        sys.stdout.write("\n")
        sys.stdout.flush()
        pass

# Function to calculate the MD5 hash of a file. This can be used to check if the XML file was updateds. 
# Takes file name as parameter (e.g. the XML file)
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Function to make API calls to FMC
# Takes multiple parameters to be used for the API call
def APIcaller(object_id, objectgroup_name, object_type, objectgroup_type, put_list, object_field):
	# Disable warnings regarding Certs. Caution: please use certs for better security
	requests.packages.urllib3.disable_warnings()

	# input FMC management IP
	server = "https://<INPUT FMC IP HERE>"   # INPUT REQUIRED

	# input FMC username (Tip: create a separate admin account for this function, otherwise user will be logged out during API calls)
	username = "<INPUT USERNAME HERE"   # INPUT REQUIRED
	if len(sys.argv) > 1:
		username = sys.argv[1]

	# input FMC password
	password = "<INPUT PASSWORD HERE"   # INPUT REQUIRED
	if len(sys.argv) > 2:
		password = sys.argv[2]

	# initiate r for the API request
	r = None
	headers = {'Content-Type': 'application/json'}
	api_auth_path = "/api/fmc_platform/v1/auth/generatetoken"
	auth_url = server + api_auth_path
	try:
		######### !IMPORTANT! 2 ways of making a REST call are provided: !IMPORTANT! #########
		# One with "SSL verification turned off" and the other with "SSL verification turned on".
		# The one with "SSL verification turned off" is uncommented. If you like to use the other then
		# uncomment the line where "verify='/path/to/ssl_certificate'"" and comment the line with "verify=False" 
		
		# REST call with SSL verification turned off (NOT RECOMMENDED, TESTING ONLY):
		r = requests.post(auth_url, headers=headers, auth=requests.auth.HTTPBasicAuth(username,password), verify=False)
		
		# REST call with SSL verification turned on: Download SSL certificates from your FMC first and provide its path for verification (RECOMMENDED)
		#r = requests.post(auth_url, headers=headers, auth=requests.auth.HTTPBasicAuth(username,password), verify='/path/to/ssl_certificate')
		
		# generate an authetication token
		auth_headers = r.headers
		auth_token = auth_headers.get('X-auth-access-token', default=None)
		if auth_token == None:
			print("auth_token not found. Exiting...")
			sys.exit()
	except Exception as err:
		print ("Error in generating auth token --> "+str(err))
		sys.exit()

	headers['X-auth-access-token']=auth_token

	# Define API path by using parameters that were passed in function to complete. 
	domain_ID = "<INPUT DOMAIN ID HERE>"   # INPUT REQUIRED
	
	# combine different elements for API path
	api_path = "/api/fmc_config/v1/domain/" + domain_ID + "/object/" + objectgroup_type + "s/" + object_id    
	url = server + api_path
	if (url[-1] == '/'):
	    url = url[:-1]
	 

	# create empty dictionary and list, to form JSON later
	object_dict = {}
	group_list = []

	# loop through list and put in right format for API call, all fields come from passed parameters in function
	for element in put_list:
		object_dict["type"] = object_type
		object_dict[object_field] = element 
		group_list.append(object_dict.copy())

	# create empty dictionary to finish JSON format
	put_data = {}

	# add fields to dictionary, to finish the JSON needed to pass to FMC with API call
	put_data["id"] = object_id
	put_data["name"] = objectgroup_name
	put_data["type"] = objectgroup_type
	put_data["literals"] = group_list

	try:
	    # REST call with SSL verification turned off (NOT RECOMMENDED, TESTING ONLY)
	    r = requests.put(url, data=json.dumps(put_data), headers=headers, verify=False)
	    # REST call with SSL verification turned on (RECOMMENDED)
	    #r = requests.put(url, data=json.dumps(put_data), headers=headers, verify='/path/to/ssl_certificate')
	    status_code = r.status_code
	    resp = r.text
	    if (status_code == 200):
	        print("PUT request was successful, output below:\n")
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

# end of script
