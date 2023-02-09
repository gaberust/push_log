from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

import requests

from datetime import datetime
from math import ceil
from secrets import token_hex

from django.views.decorators.csrf import csrf_exempt

from pushlog.models import Device, Report
from push_log.settings import PUSHOVER_APP_KEY, PUSHOVER_USER_KEY


def login_page(request):
    context = {}
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('reports')
        if 'next' in request.GET:
            context['next'] = request.GET['next']
        return render(request, template_name='login.html', context=context)
    if request.method == 'POST':
        if user := authenticate(username=request.POST.get('username'), password=request.POST.get('password')):
            login(request, user)
            return redirect(request.POST.get('next', 'reports'))
        context['username'] = request.POST.get('username')
        context['password'] = request.POST.get('password')
        context['login_failed'] = True
        return render(request, template_name='login.html', context=context)


@login_required
def index(request):
    return redirect('reports')


@login_required
def reports(request):
    # Start context object and build query args
    context = {
        'limit': int(request.GET.get('limit', 50)),
        'page': int(request.GET.get('page', 1)),
        'start_date': request.GET.get('start_date'),
        'end_date': request.GET.get('end_date'),
        'device_id': request.GET.get('device_id')
    }
    query_args = {}
    if context['start_date']:
        query_args['drop_off__gte'] = datetime.strptime(context['start_date'], '%m-%d-%Y')
    if context['end_date']:
        query_args['pick_up__lte'] = datetime.strptime(context['end_date'], '%m-%d-%Y')
    if context['device_id']:
        query_args['device_id'] = context['device_id']

    # Validate page is within bounds ( 1 <= page <= max_page )
    results = Report.objects.filter(**query_args).order_by('-reported_at')
    context['total'] = results.count()
    context['max_page'] = ceil(context['total'] / context['limit'])
    context['page'] = max(1, min(context['page'], context['max_page']))

    # Check if previous and next page buttons should be displayed
    if context['page'] > 1:
        context['prev_page'] = context['page'] - 1
    if context['page'] < context['max_page']:
        context['next_page'] = context['page'] + 1

    # Slice results
    start_index = context['limit'] * (context['page'] - 1)
    context['results'] = results[start_index:start_index + context['limit']]

    return render(request, template_name='reports.html', context=context)


@login_required
def devices(request):
    if request.method == 'GET':
        return render(request, template_name='devices.html', context={'devices': Device.objects.all()})
    if request.method == 'POST':
        device_name = request.POST.get('name', '').strip()
        if not device_name:
            return render(request, template_name='devices.html',
                          context={'devices': Device.objects.all(), 'empty_name': True})
        Device.objects.create(name=device_name, key=token_hex(64))
        return redirect('devices')


@login_required
def regenerate_device_key(request):
    if request.method == 'POST':
        if device := Device.objects.get(pk=int(request.POST.get('device_id', 0))):
            device.key = token_hex(64)
            device.save()
        return redirect('devices')


@login_required
def edit_device_name(request):
    if request.method == 'POST':
        device_name = request.POST.get('device_name', '').strip()
        if not device_name:
            return render(request, template_name='devices.html',
                          context={'devices': Device.objects.all(), 'empty_name': True})
        if device := Device.objects.get(pk=int(request.POST.get('device_id', 0))):
            device.name = device_name
            device.save()
        return redirect('devices')


@login_required
def delete_device(request):
    if request.method == 'POST':
        if device := Device.objects.get(pk=int(request.POST.get('device_id', 0))):
            device.delete()
        return redirect('devices')


@login_required
def account(request):
    return render(request, template_name='account.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        if user := authenticate(username=request.user.username, password=request.POST.get('current_password', '')):
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            if new_password == confirm_password:
                if len(new_password.strip()) > 0:
                    user.set_password(new_password)
                    user.save()
                    return render(request, template_name='account.html', context={'password_success': True})
                return render(request, template_name='account.html',
                              context={'error_message': 'New password cannot be blank.'})
            return render(request, template_name='account.html', context={'error_message': 'Passwords don\'t match.'})
        return render(request, template_name='account.html', context={'error_message': 'Invalid password.'})
    return redirect('account')


def log_out(request):
    if request.method == 'POST':
        logout(request)
    return redirect('index')


@csrf_exempt
def post_report(request):
    if device := Device.objects.get(pk=int(request.POST.get('device_id'))):
        if device.key == request.POST.get('key'):
            report = device.report_set.create(message=request.POST.get('message'))
            requests.post('https://api.pushover.net/1/messages.json', json={
                'token': PUSHOVER_APP_KEY,
                'user': PUSHOVER_USER_KEY,
                'message': report.message,
                'priority': 1,
                'title': str(device)
            })
            return HttpResponse(status=200)
    return HttpResponse(status=401)
