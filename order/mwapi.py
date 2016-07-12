from django.conf import settings

import requests
from requests.auth import HTTPBasicAuth

def pi_api_get(sufix):
	url = 'https://'+settings.PIADDR+'/webacs/api/v1'+sufix
	return requests.get(url, auth=HTTPBasicAuth(settings.PIUSER, settings.PIPASS), verify=False)
	
def pi_api_put(sufix, arguments):
	url = 'https://'+settings.PIADDR+'/webacs/api/v1'+sufix
	return requests.put(url, auth=HTTPBasicAuth(settings.PIUSER, settings.PIPASS), verify=False, data=arguments, headers={"Content-Type":"application/json"})

def pi_api_post(sufix, arguments):
	url = 'https://'+settings.PIADDR+'/webacs/api/v1'+sufix
	return requests.post(url, auth=HTTPBasicAuth(settings.PIUSER, settings.PIPASS), verify=False, data=arguments, headers={"Content-Type":"application/json"})

def get_ap_id(apmac):
	response=pi_api_get('/data/AccessPointDetails.json?ethernetMac="'+apmac+'"')
	response_json=response.json()
	if response_json['queryResponse']['@count'] == '0':
		return ""
	else:
		return response_json['queryResponse']['entityId'][0]['$']

def get_ap_status(apmac):
	ap_id=get_ap_id(apmac)
	if ap_id == "":
		return None
	else:
		response=pi_api_get('/data/AccessPointDetails/'+ap_id+'.json')
		response_json=response.json()
		status = {
			'name': response_json['queryResponse']['entity'][0]['accessPointDetailsDTO']['name'],
			'adminStatus': response_json['queryResponse']['entity'][0]['accessPointDetailsDTO']['adminStatus'],
			'apGroupName': response_json['queryResponse']['entity'][0]['accessPointDetailsDTO']['unifiedApInfo']['apGroupName']	
			}
		if status['adminStatus']=="up":
			status['controllerIPAddress']=response_json['queryResponse']['entity'][0]['accessPointDetailsDTO']['unifiedApInfo']['controllerIpAddress']
		return status

def is_apgroup_deployed(customer_id,wlc_pi_id):
	response=pi_api_get('/data/WlanControllerDetails/'+wlc_pi_id+'.json')
	response_json=response.json()
	for apgroup in response_json['queryResponse']['entity'][0]['wlanControllerDetailsDTO']['apGroups']['apGroup']:
		if 'APG'+str(customer_id) == apgroup['apGroupName']:
			return True
	return False

def is_wlan_deployed(customer_id,wlc_pi_id):
	response=pi_api_get('/data/WlanProfiles.json?controllerId="'+str(wlc_pi_id)+'"&profileName="WP'+str(customer_id)+'"')
	response_json=response.json()
	if response_json['queryResponse']['@count']=="1":
		return True
	return False

def get_device_id(device):
	response=pi_api_get('/data/Devices.json?ipAddress="'+device+'"')
	response_json=response.json()
	device_pi_id=response_json['queryResponse']['entityId'][0]['$']
	return device_pi_id

def get_wlc_list():
	response=pi_api_get('/data/WlanControllerDetails.json')
	response_json=response.json()
	wlc_list=[]
	count=int(response_json['queryResponse']['@count'])
	i=0
	while i<count:
		wlc_url='/data/WlanControllerDetails/'+response_json['queryResponse']['entityId'][i]['$']+'.json'
		#raise Exception(wlc_url)
		wlc_response = pi_api_get(wlc_url)
		#raise Exception(wlc_response)
		wlc_response_json =  wlc_response.json()
		wlc_list.append({'name':wlc_response_json['queryResponse']['entity'][0]['wlanControllerDetailsDTO']['name'],'ip':wlc_response_json['queryResponse']['entity'][0]['wlanControllerDetailsDTO']['ipAddress']})
		i=i+1
	return wlc_list

def get_wlc_id(wlc):
	response=pi_api_get('/data/WlanControllerDetails.json?ipAddress="'+wlc+'"')
	response_json=response.json()
	if response_json['queryResponse']['@count'] == "0":
		return None
	wlc_pi_id=response_json['queryResponse']['entityId'][0]['$']
	return wlc_pi_id

def is_customer_deployed(customer_id, wlc):
	wlc_pi_id=get_wlc_id(wlc)
	if wlc_pi_id:
		if is_apgroup_deployed(customer_id,wlc_pi_id) & is_wlan_deployed(customer_id,wlc_pi_id):
			return True
	return False
	
def get_template_id(template_name):
	response=pi_api_get('/data/CLITemplate/'+template_name+'.json?name="'+template_name+'"')
	response_json=response.json()
	return response_json['queryResponse']['entityId'][0]['$']
	
def deploy_cli_template(template_name, template_args, wlc):
	#template_id=get_template_id(template_name)
	device_pi_id=get_device_id(wlc)
	arguments='\
		{\
  			"cliTemplateCommand" : {\
  				"templateName" :"'+template_name+'",\
    			"targetDevices" : {\
      				"targetDevice" : {\
        				"targetDeviceID" :"'+device_pi_id+'",\
        				"variableValues" : {'
	for name,value in template_args.items():
		arguments=arguments+'"variableValue": {"name" : "'+name+'", "value" :"'+str(value)+'"},'
	arguments=arguments+'\
      					}\
    				},\
  				}\
  			}\
		}'
	#raise Exception(arguments)
	#output=pi_api_put("/op/cliTemplateConfiguration/deployTemplateThroughJob.json", arguments)
	output=pi_api_put("/op/cliTemplateConfiguration/deploy.json", arguments)

def deploy_ap_group(apgroup, wlanprofile, wlc):
	wlc_pi_id=get_wlc_id(wlc)
	arguments='\
		{\
			"apGroupMembershipDTO" : {\
			"controllerId" : '+wlc_pi_id+',\
			"apGroupName" : "'+apgroup+'",\
			"apGroupProfileMappings" : {\
      			"apGroupProfileMapping" : {\
        			"interfaceName" : "management",\
        			"nacOverride" : false,\
        			"wlanProfileName" : "'+wlanprofile+'"\
      			}\
    		},\
  			}\
		}'
	output=pi_api_post("/op/wlanProvisioning/apGroup.json", arguments)
	raise Exception(output.text)
	return
	
def modify_ap_group(apgroup, aps, wlanprofile, wlc):
	wlc_pi_id=get_wlc_id(wlc)
	arguments='\
		{\
			"apGroupMembershipDTO" : {\
			"controllerId" : '+wlc_pi_id+',\
			"apGroupName" : "'+apgroup+'",\
			"apGroupProfileMappings" : {\
      			"apGroupProfileMapping" : {\
        			"interfaceName" : "management",\
        			"nacOverride" : false,\
        			"wlanProfileName" : "'+wlanprofile+'"\
      			}\
    		},\
			"apMembers" : {'
	for a in aps:
		arguments=arguments+'"apMember": '+get_ap_id(a)+''
	arguments=arguments+'\
    			}\
  			}\
		}'
	#raise Exception(arguments)	
	output=pi_api_put("/op/wlanProvisioning/apGroup.json", arguments)
	raise Exception(output.text)
		