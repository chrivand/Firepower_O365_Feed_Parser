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
from netmiko import ConnectHandler
from pprint import pprint
from requests.auth import HTTPBasicAuth

# A class to handle communication to the Firepower Management Console (FMC) APIs
class Asa:

    def __init__(self, config_data):
        self.asa_ip     = config_data['ASA_IP']
        self.asa_user   = config_data['ASA_USER']
        self.asa_pass   = config_data['ASA_PASS']
        self.asa_objectname = config_data['ASA_OBJECTNAME']

        if not config_data['SSL_VERIFY']:
            requests.packages.urllib3.disable_warnings()
            self.ssl_verify = config_data['SSL_VERIFY']
        else:
            self.ssl_verify = config_data['SSL_CERT']

        self.doConnection()

    def doConnection(self):

        print('\nConnecting to ASA...')

        try:
            self.connection = ConnectHandler(
                                host=self.asa_ip,
                                device_type="cisco_asa",
                                username=self.asa_user,
                                password=self.asa_pass,
                                )


            print('ASA Successfully Connected.')

        except Exception as err:
            print('Error connecting to ASA: ' + str(err))
            exit()
    
    # A function to execute a single command on the ASA
    def doCommand(self, theCommand):
        
        print('\nSending ' + theCommand + ' request to ASA.')

        try:
            output = self.connection.send_command(theCommand)
            return output

        except Exception as err:
            print('Error sending command to ASA: ' + str(err))
            exit()

    def doCommands(self, theCommands):
        
        print('\nSending request to ASA:')
        print(theCommands)

        try:
            output = self.connection.send_config_set(theCommands)
            return output

        except Exception as err:
            print('Error sending commands to ASA: ' + str(err))
            exit()