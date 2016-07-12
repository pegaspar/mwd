from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.new, name='new'),
    url(r'^login/$', views.login, name='login'),
    url(r'^(?P<customer_id>[0-9]+)/view/$', views.customer_view, name='customer_view'),
    url(r'^(?P<customer_id>[0-9]+)/(?P<ap_id>[0-9]+)/ap_update/$', views.ap_update, name='ap_update'),
    url(r'^(?P<customer_id>[0-9]+)/(?P<ap_id>[0-9]+)/ap_clear/$', views.ap_clear, name='ap_clear'),
    url(r'^(?P<customer_id>[0-9]+)/(?P<ap_id>[0-9]+)/ap_deploy/$', views.ap_deploy, name='ap_deploy'),
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^admin/(?P<customer_id>[0-9]+)/update/$', views.admin_customer_update, name='admin_customer_update')
]