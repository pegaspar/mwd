from re import match

from .mwapi import get_ap_status, is_customer_deployed, deploy_cli_template, get_wlc_list, modify_ap_group, deploy_ap_group

from .models import Customer, AP

def valid_mac(mac):
	return match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac)
	
def valid_ip(ip):
	a = ip.split('.')
	if len(a) != 4:
		return False
	for x in a:
		if not x.isdigit():
			return False
		i = int(x)
		if i < 0 or i > 255:
			return False            
	return True
	
def valid_aaaindex(index):
	return True

def mwapp_sync_ap_status(ap):
	
	customer = ap.customer
	if customer.status < 2 or not valid_mac(ap.mac):
		ap.status = 0
		ap.save()
		return
		
	ap_network_status = get_ap_status(ap.mac)
	if ap_network_status == None:
		ap.status = 1 #valid mac, customer provisioned, ap not connected
		ap.save()
		return
	elif ap_network_status['apGroupName'] == 'APG'+str(customer.pk):
		ap.status = 3 #connected and within right group - ready to serve
		ap.save()
		return
	else:
		ap.status = 2 # connected but within Out-of-Box or other group
		ap.save()
		return
	return
	
def mwapp_sync_customer_status(customer):
	if not valid_ip(customer.wlc) or not valid_aaaindex(customer.aaa_ip):
		customer.status=0
	else:
		if customer.status==0 and valid_ip(customer.wlc) and valid_aaaindex(customer.aaa_ip):
			customer.status=1
		if customer.status > 0:
			if is_customer_deployed(customer.pk, customer.wlc):
				customer.status=2
			else:
				customer.status=1
	customer.save();	
	return
	
def mwapp_deploy_ap_to_group(ap):
	groupcustomer = ap.customer
	ap_status=get_ap_status(ap.mac)
	groupAPs = [a.mac for a in AP.objects.filter(customer=groupcustomer).filter(status="3")]
	groupAPs.append(ap.mac)
	##deploy_cli_template("AP to Group", {"APG": "APG"+str(customer.pk), "AP": ap_status["name"]}, customer.wlc)
	modify_ap_group("APG"+str(groupcustomer.pk), groupAPs, 'WP'+str(groupcustomer.pk), groupcustomer.wlc)
	##add AP to PI site
	
def mwapp_get_wlc_list():
	return get_wlc_list()	
	
def mwapp_create_customer(customer_name, customer_email, customer_ssid, customer_aps):
	new_customer = Customer(name=customer_name,email=customer_email, ssid=customer_ssid)
	new_customer.save()
	i = customer_aps
	while i>0:
		new_ap = AP(customer=new_customer)
		new_ap.save()
		i = i-1
	# Send email to admin about new customer
	send_mail('New customer order: '+request.POST['customer_name'], 'Dear admin!\n\n\
Please provision following for the new customer:\n\n\
- GlobalReach account and portal, note the user credentials, AAA server IP, AAA secret and Redirect URL\n\
- Prime Infrastructure account, note the user credentials\n\
- Check, assign and note the WLC to be used for the customer\n\n\
After you have finished the preparation, go to '+request.build_absolute_uri(reverse('order:admin'))+', fill-in the data and initiate customer deployment.\
\n\n\
Yours,\n\
Managed WiFi Dashboard\
		', 'pegaspar7@gmail.com', ['pegaspar@cisco.com'], fail_silently=False)
	return
	
def mwapp_deploy_customer(customer):
	#create site on PI
	
	# Create WP
	deploy_cli_template('Create_WP', {'WPID': customer.pk, 'WPNAME': 'WP'+str(customer.pk), 'SSID': customer.ssid, 'AAAID': '1'}, customer.wlc)
	
	# Create APG with WP
	deploy_ap_group('APG'+str(customer.pk),'WP'+str(customer.pk),customer.wlc)
	
	return	