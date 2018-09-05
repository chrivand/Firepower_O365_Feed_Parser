# Firepower O365 Feed Parser 
# ***Updated Script with NEW O365 Web Service API***

_This is a Sample Script that can parse the NEW O365 Web Service API and upload it to Firepower Management Center as Group Objects._

---

This is a sample script that parses the NEW O365 Web Service API (https://docs.microsoft.com/en-us/office365/enterprise/managing-office-365-endpoints#webservice) that Microsoft publishes with URL, IPv4 and IPv6 addresses. These addresses are used for the infrastructure of the Microsoft cloud applications (e.g. Office 365). The script will parse the NEW O365 Web Service API into 2 separate lists and use the FMC API's to upload them into 2 Group Objects. These Group Objects can be used in a Firepower trust/prefilter rule. By doing so the traffic is excluded from further inspection, to prevent latency issues with the Microsoft O365 applications. 

Please contact me if you have any questions or remarks. If you find any bugs, please report them to me, and I will correct them (or do a pull request).

## Features

* Retrieving Wordlwide URLs and IPs from new O365 REST-based web service. 
* Parsing these into 2 flat lists (URL and IP);
* Creating right JSON format for FMC API PUT requests;
* Uploading this JSON to FMC, overwriting the previous Group Object;
* Checking if O365 file was updated, using the O365 Version API Endpoint;
* Continuously checking for updates with a specified time interval (optional).

### Potential next steps

* Email / Webex Teams alert when changes were made to Objects;
* Automatic policy deploy using API when changes were made to Objects;
* Create extra modules for other SaaS applications;
* Create extra modules for other Cisco solutions (WSA, Umbrella etc.).


## Solution Components

The script consists of 2 python files. The main script can run indefinitely, leveraging a function that is built in, to rerun the script every x amount of seconds (it can also just be executed once). Then, using the Version API Endpoint, the script checks if changes were made to the Web Service list. If changes were made, the Web Service list is parsed and uploaded using a PUT request to FMC. Microsoft updates the Office 365 IP address and FQDN entries at the end of each month and occasionally out of cycle for operational or support requirements. Therefore, Microsoft recommends you check the version daily, or at the most, hourly. This can be automated with the script.

### Cisco Products / Services

* Cisco Firepower Management Center;
* Cisco Firepower Threat Defense NGFW.


## Installation

These instructions will enable you to download the script and run it, so that the output can be used in Firepower as Group Objects. What do you need to get started? Please find a list of tasks below:

1. You need the IP address (or domain) of the FMC, the username and password. These need to be added to the APIcaller function and are obviously also needed to access the FMC (and FMC API explorer). It is recommended to create a separate FMC login account for the API usage, otherwise the admin will be logged out during every API calls. 

2. Create 2 Group Objects in FMC: *"O365_Web_Service_URLs"* (URL Group Object) and *"O365_Web_Service_IPs"* (Network Group Object). At first you will have to put in a random URL/Network, to create the group objects. No worries, we will override this later.

3. In FMC, go to System > Configuration > REST API Preferences to make sure that the REST API is enabled on the FMC.

4. Use the FMC API Explorer to do a GET request for the Group Objects. This is done by going into the FMC API Explorer (can be reached at https://IP-addressOfFMC/api/api-explorer), and then clicking on *"Object"* in the left menu. The scroll down to *"networkgroups"* and click on *"GET"* and then again on *"GET"* in the right menu. 

5. Now you will need to copy-paste the the Object ID's of the Network Group Object (*"O365_Web_Service_IPs"*). The ID's will look like the following format: *"000XXXX-YYYY-ZZZZ-0000-01234567890"*. This is displayed in the *"Response Text"* output box in the right menu. You will need these later in the PUT requests to update the objects. Below is an example of how this output would look for the *"O365_Web_Service_IPs"* Network Group Object:

```
"type": "NetworkGroup",
"name": "O365_Web_Service_IPs",
"id": "000XXXX-YYYY-ZZZZ-0000-01234567890"
```

6. You will also need the ID for the FMC Domain, to include in the API path. This can also be obtained from the FMC API explorer. When clicking on GET when doing to request above, the ID of the domain is showed in the path and has the same syntax as the Object ID's: 

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/screenshotAPIexplorer.png)

7. Repeat the GET request of step 4 as well for *"urlgroups"*, to obtain the ID for the URL Group Object (*"O365_Web_Service_URLs"*). You should now have 3 ID's copy-pasted, which you can put inside the APIcaller function and in the O365WebServiceParser function.

8. It is also recommended to download a SSL certificate from FMC and put it in the same folder as the scripts. This will be used to securely connect to FMC. In the APIcaller function, there is an option to enable SSL verification that uses this certificate. It has clear instructions commented above the code.

9. More instructions are in comments in the 2 sample scripts. It will say *### INPUT REQUIRED ###* after the variables where you are required to fill in the FMC IP, the FMC login, the Domain ID and the Group Object ID's. All of these fields are in the APIcaller function (FMC IP, Domain ID and login) and O365WebServiceParser function (2 Group Object ID's).


### How to use the Group Objects in Firepower Management Center.

For better understanding of the packet flow in Firepower Threat Defense, and how the Fastpath action in the Prefilter Policy works, please review the following flow diagram:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/packetflowftd.png)

After the successful PUT requests, the 2 Group Objects will have been updated with the new IP-addresses and URLs. Please find screenshots of the 2 Group Objects, after the API call:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/screenshot_urlobject_new.png)

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/screenshot_networkobject_new.png)

These objects can be used in either Prefilter Policy Fastpath-rule (for the Network Object), or in an Access Control Policy Trust-rule (for the URL Object). This is an example of how to configure the Prefilter Policy rule in FMC:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/addprefilterrule.png)

This will result in the following rule:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/fastpathrule.png)

Likewise, this can be done with a Trust Rule in the Access Control Policy for the URL Group Object:

![Networkobjects](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/master/screenshots_FMC_O365/trustrule.png)

As a final step you will need to do a Policy Deploy, each time that the Group Objects have been updated. This can be done from the FMC by clicking on *"DEPLOY"* and by selecting the device that need this Policy Deploy.

### Please take caution on the following notes:

* Please be aware that a policy redeploy is needed to update the Group Objects in the used Policies. Currently there is no API call built in to do a policy redeploy, since this might cause other unfinished policies or objects to be deployed (e.g. if a network administrator is working on a Policy in the GUI).

* Important is to use SSL verification and to test the script before running this in a production environment.

* Please test this properly before implementing in a production environment. This is a sample script.

* In case the intervalScheduler is used: the running script should be hosted in a secure environment! For example: if a malicious actor can place additional IP-addresses or URL's in the list somehow, they will be put in a Firepower trust rule, and might cause the malicious actor to bypass security.


## Author(s)

* Christopher van der Made (Cisco)
