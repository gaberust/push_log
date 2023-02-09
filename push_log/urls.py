"""push_log URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import re_path

import pushlog.views

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path(r'login/?$', pushlog.views.login_page, name='login_page'),
    re_path(r'', pushlog.views.index, name='index'),
    re_path(r'reports/?$', pushlog.views.reports, name='reports'),
    re_path(r'devices/?$', pushlog.views.devices, name='devices'),
    re_path(r'edit_device/?$', pushlog.views.edit_device_name, name='edit_device_name'),
    re_path(r'regenerate_key/?$', pushlog.views.regenerate_device_key, name='regenerate_device_key'),
    re_path(r'delete_device/?$', pushlog.views.delete_device, name='delete_device'),
    re_path(r'account/?$', pushlog.views.account, name='account'),
    re_path(r'change_password/?$', pushlog.views.change_password, name='change_password'),
    re_path(r'logout/?$', pushlog.views.log_out, name='log_out'),
    re_path(r'post_report/?$', pushlog.views.post_report),
]
