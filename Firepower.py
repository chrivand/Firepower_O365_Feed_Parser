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

# Import Libraries
import json
import requests
from requests.auth import HTTPBasicAuth

# A class to handle communication to the Firepower Management Console (FMC) APIs
class Firepower:

    def __init__(self, config_data):
        self.fmc_ip     = config_data['FMC_IP']
        self.fmc_user   = config_data['FMC_USER']
        self.fmc_pass   = config_data['FMC_PASS']

        if not config_data['SSL_VERIFY']:
            requests.packages.urllib3.disable_warnings()
            self.ssl_verify = config_data['SSL_VERIFY']
        else:
            self.ssl_verify = config_data['SSL_CERT']

        self.getAuthToken()

    def getAuthToken(self):

        print('\nFetching Authentication Token from FMC...')

        # Build HTTP Authentication Instance
        auth = HTTPBasicAuth(self.fmc_user, self.fmc_pass)

        # Build HTTP Headers
        auth_headers = {'Content-Type': 'application/json'}

        # Build URL for Authentication
        auth_url = "https://{}/api/fmc_platform/v1/auth/generatetoken".format(self.fmc_ip)

        try:
            http_req = requests.post(url=auth_url, auth=auth, headers=auth_headers, verify=self.ssl_verify)

            print('FMC Auth Response: ' + str(http_req.headers))

            # Set the Auth Token and FMC Domain UUID
            self._auth_token = http_req.headers.get('X-auth-access-token', default=None)
            self.fmc_domain = http_req.headers.get('DOMAIN_UUID', default=None)

            # If we didn't get a token, then something went wrong
            if self._auth_token == None:
                print('Authentication Token Not Found.  Exiting...')
                exit()

            print('Authentication Token Successfully Fetched.')

        except Exception as err:
            print('Error fetching auth token from FMC: ' + str(err))
            exit()
    
    # A function to modify an Object in the FMC
    def doApiCall(self, method, endpoint, json_data=None):
        
        print('\nSending ' + str(method) + ' request to ' + str(endpoint) + ' endpoint on the FMC.')

        # If there's no FMC Authentication Token, then fetch one
        if self._auth_token == '':
            self.getAuthToken()

        # Build URL for Object endpoint
        endpoint_url = "https://{}/api/fmc_config/v1/domain/{}/{}".format(self.fmc_ip, self.fmc_domain, endpoint)

        # Build new headers with the access token
        headers = {'Content-Type': 'application/json', 'X-auth-access-token': self._auth_token}

        try:
            # Take the appropriate action - GET by default
            if method is 'POST':
                http_req = requests.post(url=endpoint_url, headers=headers, json=json_data, verify=self.ssl_verify)
            elif method is 'PUT':
                http_req = requests.put(url=endpoint_url, headers=headers, json=json_data, verify=self.ssl_verify)
            elif method is 'DELETE':
                http_req = requests.delete(url=endpoint_url, headers=headers, json=json_data, verify=self.ssl_verify)
            else:
                http_req = requests.get(url=endpoint_url, headers=headers, json=json_data, verify=self.ssl_verify)

            # Check to make sure the POST was successful
            if http_req.status_code >= 200 and http_req.status_code < 300:
                print('Request succesfully sent to FMC.')
                #print('HTTP Response: ' + str(http_req.text))
                return http_req.json()
            else:
                print("FMC Connection Failure - HTTP Return Code: {}\nResponse: {}".format(http_req.status_code, http_req.json()))
                exit()

        except Exception as err:
            print('Error posting request to FMC: ' + str(err))
            exit()
        finally:
            if http_req: http_req.close()

    # Create an object in the FMC
    def createObject(self, object_endpoint, object_json):

        # Build the object specific URL
        object_url = "object/" + object_endpoint

        print("\nCreating object at the following endpoint: " + object_url)

        # Send the JSON to the FMC
        return_json = self.doApiCall('POST', object_url, object_json)

        return return_json
    
    # Delete an object in the FMC
    def deleteObject(self, object_endpoint, object_uuid):

        # Build the object specific URL
        object_url = "object/" + object_endpoint + '/' + object_uuid

        print("\nDeleting the following object: " + object_url)

        return_json = self.doApiCall('DELETE', object_url)

        return return_json
    
    # Get an object from the FMC
    def getObject(self, object_endpoint, object_uuid=None):

         # Build the object specific URL
        object_url = "object/" + object_endpoint + '/' + object_uuid

        print("\nRetrieving object from FMC: " + object_url)

        # Get the object data
        return_json = self.doApiCall('GET', object_url)

        return return_json

    # Update an object in the FMC
    def updateObject(self, object_endpoint, object_uuid, object_json):

        # Build the object specific URL
        object_url = "object/" + object_endpoint + '/' + object_uuid

        print("\nUpdating object at the following endpoint:  " + object_url)

        # PUT the object JSON data
        return_json = self.doApiCall('PUT', object_url, object_json)

        return return_json

    # Get Pending Deployments
    def getPendingDeployments(self):

        # Build the deployment specific URL
        deployment_url = "deployment/deployabledevices?expanded=true"

        # GET teh deployment JSON data
        return_json = self.doApiCall('GET', deployment_url)

        return return_json

    # Trigger Deployments
    def postDeployments(self, deployment_json):

        # Build the deployment specific URL
        deployment_url = "deployment/deploymentrequests"

        # GET teh deployment JSON data
        return_json = self.doApiCall('POST', deployment_url, deployment_json)

        return return_json