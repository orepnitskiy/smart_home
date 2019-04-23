import json
from .models import Setting
import requests
from django.core.mail import send_mail
from coursera_house.settings import SMART_HOME_ACCESS_TOKEN, SMART_HOME_API_URL
from coursera_house.settings import EMAIL_RECEPIENT, EMAIL_HOST_USER


def get_user_data():
    """ Function that gets real-time data from smart home API """
    json_user_data = requests.get(f'{SMART_HOME_API_URL}/user.controller', headers = {
    'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
    }
    )
    rsp_data = json.loads(json_user_data.text)
    user_data = rsp_data["data"]
    return user_data
    
    
def curtains_manage(close):
    """ Function that close or open curtains """
   value = "close" if close else "open"
   requests.post(f'{SMART_HOME_API_URL}/user.controller', headers = {
            'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
            }, data=json.dumps({
            "controllers": [
            {
            "name": "curtains",
            "value": value
            }
            ]
            }))
            
   
def smart_home_manager():
    """ Function, that process and send data to the smart home API, according to the documentation """
    hot_water_target_temperature = Setting.objects.get(controller_name='hot_water_target_temperature').value
    bedroom_target_temperature = Setting.objects.get(controller_name="bedroom_target_temperature").value
    bedroom_light = Setting.objects.get(controller_name='bedroom_light').value
    bathroom_light = Setting.objects.get(controller_name='bathroom_light').value
    bedroom_light = True if bedroom_light == '1' else False
    bathroom_light = True if bathroom_light == '1' else False
    user_data = get_user_data()
    for x in user_data:
        if x['name'] == 'leak_detector' and x['value']:
            send_mail(
            'Leak detected in your house!',
            'We did everything we can to prevent effects of the leak. We ask you to do something to prevent leak',
            EMAIL_HOST_USER,
            [EMAIL_RECEPIENT]
            )

            requests.post(f'{SMART_HOME_API_URL}/user.controller', headers = {
            'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
            }, data=json.dumps({
            "controllers": [
            {
            "name": "cold_water",
            "value":False
            },
            {
            'name': "hot_water",
            'value': False
            }
            ]
            }))
    user_data = get_user_data()
    for x in user_data:
        if x['name'] == 'cold_water' and not x['value']:
            cold_water = False
            requests.post(f'{SMART_HOME_API_URL}/user.controller', headers = {
            'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
            }, data=json.dumps({
            "controllers": [
            {
            "name": "boiler",
            "value": False
            },
            {
            'name': "washing_machine",
            'value': False
            }
            ]
            }))
        elif x['name'] == "cold_water":
            cold_water = True
    for x in user_data:
        if x['name'] == 'smoke_detector' and x['value']:
            smoke_detector = True
            bedroom_light, bathroom_light = False, False
            requests.post(f'{SMART_HOME_API_URL}/user.controller', headers = {
            'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
            }, data=json.dumps({
            "controllers": [
            {
            "name": "air_conditioner",
            "value": False
            },
            {
            'name': "bedroom_light",
            'value': False
            },
            {
            'name': "bathroom_light",
            'value': False
            },
            {
            'name': "boiler",
            'value': False
            },
            {
            'name': "washing_machine",
            'value':'off'
            }
            ]
            }))
    for x in user_data:

        if x['name'] == 'boiler_temperature':
            boiler_temperature = x['value']
    try:
        if boiler_temperature < hot_water_target_temperature*0.9 and not smoke_detector and cold_water:
               requests.post(f'{SMART_HOME_API_URL}/user.controller', headers = {
                'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
              }, data=json.dumps({
                "controllers": [
                {
                'name': "boiler",
                'value': True
                }
                ]
                }))
        elif boiler_temperature >= hot_water_target_temperature*1.1 and not smoke_detector and cold_water:
            requests.post(f'{SMART_HOME_API_URL}/user.controller', headers = {
                'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
                }, data=json.dumps({
                "controllers": [
                {
                'name': "boiler",
                'value': False
                }
                ]
                }))
    except TypeError:
        pass
    user_data = get_user_data()
    for x in user_data:
       if x['name'] == 'curtains' and x['value'] == 'sightly_open':
           curtains_manual_manage = True
       else:
           curtains_manual_manage = False
    for x in user_data:
        if x['name'] == 'outdoor_light':
            outdoor_light = x['value']
        elif x["name"] == "bedroom_temperature":
            bedroom_temperature = x["value"]
    if outdoor_light < 50 and not curtains_manual_manage and not bedroom_light:
        curtains_manage(close = True)
    if outdoor_light > 50 or bedroom_light and not curtains_manual_manage:
        curtains_manage(close = False)
    if bedroom_temperature > bedroom_target_temperature*1.1 and not smoke_detector:
            requests.post(f'{SMART_HOME_API_URL}/user.controller', headers = {
            'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
            }, data=json.dumps({
            "controllers": [
            {
            "name": "air_conditioner",
            "value": True
            }
            ]
            }))
    elif bedroom_temperature < bedroom_target_temperature*0.9:
            requests.post(f'{SMART_HOME_API_URL}/user.controller', headers = {
            'Authorization':f'Bearer {SMART_HOME_ACCESS_TOKEN}'
            }, data=json.dumps({
            "controllers": [
            {
            "name": "air_conditioner",
            "value": False
            }
            ]
            }))
