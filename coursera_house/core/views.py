from django.urls import reverse_lazy
from django.views.generic import FormView
import requests
from .models import Setting
from .form import ControllerForm
import json
from django.http import HttpResponse
from coursera_house.settings import SMART_HOME_ACCESS_TOKEN, SMART_HOME_API_URL
from coursera_house.core.tasks import smart_home_manager

class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')
    
    
    @staticmethod
    def get_status():
        """ Getting information from smart home API """
        rsp = requests.get(f'{SMART_HOME_API_URL}/user.controller', headers = {
        'Authorization' : f'Bearer {SMART_HOME_ACCESS_TOKEN}'
        }
        )
        rsp_data = json.loads(rsp.text)["data"]
        data = {rsp_data[i]['name']:rsp_data[i]['value'] for i in range(len(rsp_data))}
        return data
    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = self.get_status()
        return context

    def get_initial(self):
        initial = super(ControllerView, self).get_initial()
        initial['bedroom_target_temperature'] = 21
        initial['hot_water_target_temperature'] = 80
        return initial
        
     
    @staticmethod
    def create_model(form_data):
        """ Creating model if form was sent first time """
        bedroom = 1 if form_data['bedroom_light'] else 0
        bathroom = 1 if form_data['bathroom_light'] else 0
        hot_water = Setting(controller_name="hot_water_target_temperature", value=form_data["hot_water_target_temperature"])
        hot_water.save()
        bedroom_temp = Setting(controller_name="bedroom_target_temperature", value=form_data["bedroom_target_temperature"])
        bedroom_temp.save()
        bedroom_light = Setting(controller_name="bedroom_light", value=bedroom)
        bedroom_light.save()
        bathroom_light = Setting(controller_name="bathroom_light", value=bathroom)
        bathroom_light.save()
         
         
    @staticmethod
    def change_model(form_data):
        """ Change model values according to data from form """
        bedroom = 1 if form_data['bedroom_light'] else 0
        bathroom = 1 if form_data['bathroom_light'] else 0 
        Setting.objects.filter(pk=3).update(value=bedroom)
        Setting.objects.filter(pk=4).update(value=bathroom)
        Setting.objects.filter(pk=1).update(value=form_data['hot_water_target_temperature'])
        Setting.objects.filter(pk=2).update(value=form_data["bedroom_target_temperature"])
        
        
    def form_valid(self, form):
        form_data = form.cleaned_data
       
        if Setting.objects.all().count() == 0:
            self.create_model(form_data)
        else:
            self.change_model(form_data)
        hot_water_target_temperature = Setting.objects.get(controller_name='hot_water_target_temperature')
        bedroom_target_temperature = Setting.objects.get(controller_name="bedroom_target_temperature").value

        smart_home_manager()
        return super(ControllerView, self).form_valid(form)
