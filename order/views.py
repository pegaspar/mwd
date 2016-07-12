from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.urlresolvers import reverse
from django.contrib import messages

from django.core.mail import send_mail

from .models import Customer
from .models import AP

from .mwapp import mwapp_sync_customer_status, mwapp_sync_ap_status, mwapp_deploy_ap_to_group, mwapp_get_wlc_list, mwapp_create_customer, mwapp_deploy_customer


def index(request):
	customer_list = Customer.objects.order_by('name')
	context = {
		'customer_list': customer_list,
	}
	return render(request, 'order/index.html', context)


def new(request):
	if request.method == 'POST' and request.POST:
		# Create new customer
		check_customer=Customer.objects.filter(email=request.POST['customer_email'])
		if len(check_customer) > 0:
			messages.error(request, 'Customer exists.')
			return HttpResponseRedirect(reverse('order:new'))
		mwapp_create_customer(request.POST['customer_name'],request.POST['customer_email'],request.POST['customer_ssid'],request.POST['customer_aps'])
		request.session["admin"] = 0
		request.session["email"] = request.POST['customer_email']
		return HttpResponseRedirect(reverse('order:customer_view', args=(new_customer.pk,)))
	else:
		request.session["admin"] = 0
		request.session["email"] = ""
		return render(request, 'order/new.html')
		
def login(request):
	if request.POST['customer_email'] == "admin":
		request.session["admin"] = 1
		return HttpResponseRedirect(reverse('order:admin'))
	customer=Customer.objects.filter(email=request.POST['customer_email'])
	if len(customer) == 0:
		messages.error(request, 'Customer unknown.')
		return HttpResponseRedirect(reverse('order:new'))
	else:
		request.session["admin"] = 0
		request.session["email"] = request.POST['customer_email']
		return HttpResponseRedirect(reverse('order:customer_view', args=(customer[0].pk,)))
    
def customer_view(request, customer_id):
	customer = Customer.objects.get(pk=customer_id)
	if customer.email != request.session["email"]:
		if request.session["admin"] == 0:
			return HttpResponseRedirect(reverse('order:new'))
	
	customer_aps = AP.objects.filter(customer=customer)
	
	mwapp_sync_customer_status(customer)
	
	for ap in customer_aps:
		mwapp_sync_ap_status(ap)				
	
	context = {
		'customer': customer,
		'customer_aps': customer_aps,
	}
	return render(request, 'order/view.html', context)
	
def ap_update(request, customer_id, ap_id):
	change_ap = AP.objects.get(pk=ap_id)
	change_ap.status = 0
	change_ap.mac = request.POST['ap_mac']
	change_ap.save()
	return HttpResponseRedirect(reverse('order:customer_view', args=(customer_id,)))
	
def ap_clear(request, customer_id, ap_id):
	change_ap = AP.objects.get(pk=ap_id)
	change_ap.status = 0
	change_ap.mac = ""
	change_ap.save()
	return HttpResponseRedirect(reverse('order:customer_view', args=(customer_id,)))
	
def ap_deploy(request, customer_id, ap_id):
	deploy_ap = AP.objects.get(pk=ap_id)
	mwapp_deploy_ap_to_group(deploy_ap)
	return HttpResponseRedirect(reverse('order:customer_view', args=(customer_id,)))
	
def admin(request):
	customers = Customer.objects.all()
	wlc_list = mwapp_get_wlc_list()
	#raise Exception(wlc_list)
	
	for customer in customers:
		mwapp_sync_customer_status(customer)
	
	customers = customers.order_by('status')
	
	customers_with_wlcs = []
	for customer in customers:
		customer_with_list={
			'pk':customer.pk,
			'name':customer.name,
			'email':customer.email,
			'status':customer.status,
			'ssid':customer.ssid,
			'wlc':customer.wlc,		
			'portal_url':customer.portal_url,
			'aaa_ip':customer.aaa_ip,
			'aaa_port':customer.aaa_port,
			'aaa_secret':customer.aaa_secret,
			'wlc_list':[],
			'pi_user':customer.pi_user,
			'pi_password':customer.pi_password,
			'gr_user':customer.gr_user,
			'gr_password':customer.gr_password,
			'gr_customer':customer.gr_customer,
			}
		selected=0
		for wlc_check in wlc_list:
			if wlc_check['ip'] == customer.wlc:
				customer_with_list['wlc_list'].append({"name":wlc_check['name'],"ip":wlc_check['ip'],"selected":"1"})
				selected=1
			else:
				customer_with_list['wlc_list'].append({"name":wlc_check['name'],"ip":wlc_check['ip'],"selected":"0"})
		if selected==0:
			customer_with_list['wlc_list'].append({"name":customer.wlc,"ip":customer.wlc,"selected":"1"})
		customers_with_wlcs.append(customer_with_list)
	context = {
		'customers': customers_with_wlcs
	}
	return render(request, 'order/admin.html', context)
	
def admin_customer_update(request, customer_id):
	if 'update' in request.POST:
		change_customer = Customer.objects.get(pk=customer_id)
		change_customer.wlc=request.POST['wlc']
		change_customer.portal_url=request.POST['portal_url']
		change_customer.aaa_ip=request.POST['aaa_ip']
		change_customer.aaa_secret=request.POST['aaa_secret']
		change_customer.pi_user=request.POST['pi_user']
		change_customer.pi_password=request.POST['pi_password']
		change_customer.gr_user=request.POST['gr_user']
		change_customer.gr_password=request.POST['gr_password']
		change_customer.gr_customer=request.POST['gr_customer']
		change_customer.save()
	elif 'delete' in request.POST:
		delete_customer = Customer.objects.get(pk=customer_id)
		delete_customer.delete()
	else:
		deploy_customer = Customer.objects.get(pk=customer_id)
		mwapp_deploy_customer(deploy_customer)
		#deploy_cli_template("AP to APGroup",{"aa": "bbb", "cc": "ddd"},request.POST['wlc'])
	return HttpResponseRedirect(reverse('order:admin'))
	
	
	
	
	