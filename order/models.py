from django.db import models

# Create your models here.

class Customer(models.Model):
	name = models.CharField(max_length=200)
	email = models.CharField(max_length=200)
	password = models.CharField(max_length=200)
	ssid = models.CharField(max_length=200)
	portal_url = models.CharField(max_length=1000)
	aaa_ip = models.CharField(max_length=200)
	aaa_port = models.CharField(max_length=200)
	aaa_secret = models.CharField(max_length=200)
	wlc = models.CharField(max_length=200)
	pi_user = models.CharField(max_length=200,default="")
	pi_password = models.CharField(max_length=200,default="")
	gr_user = models.CharField(max_length=200,default="")
	gr_password = models.CharField(max_length=200,default="")
	gr_customer = models.CharField(max_length=200,default="")
	status = models.PositiveSmallIntegerField(default=0)
	
class AP(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	mac = models.CharField(max_length=200)
	name = models.CharField(max_length=200)
	status = models.PositiveSmallIntegerField(default=0)
	