# Smart home
For correct start of web application it's mandatory to start migrations and apply them, also change settings of email. That app interacts with API of smart home and do all functionality according to events and actions of user.

Smart home API documentation ( Available only on Russian :( ): http://smarthome.t3st.ru/docs (Available only on Russian)
Technical task is provided below:

Devices, connected to the controller are available on write (usually true - on/open, false - off/close).

# Devices (write):
air_conditioner – conditioner (true, false). 
bedroom_light – lamp in bedroom (true, false).
bathroom_light – lamp in bathroom (true, false).
curtains – curtains (“open”, “close”).
boiler – boiler (true, false).
cold_water – cold water (true, false). 
hot_water – hot water (true, false).
washing_machine – washing mashine string (“on” – вкл, “off” – выкл).  

# Датчики (чтение):
air_conditioner – conditioner. (true, false).
bedroom_temperature – Temperature in bedroom. Int (0 – 80).
bedroom_light – lamp in bedroom. (true, false).
smoke_detector – smoke detector. (true, false).
bedroom_presence – Detector of presence in bathroom (true, false).
bedroom_motion – Detector of motion in bedroom. (true, false).
curtains – curtains. string (“open”, “close”, “slightly_open” – opened manully).
outdoor_light – detector of outdoor light (0 – 100).
boiler – Бойлер. (true, false).
boiler_temperature – Temperature of hot water in boiler. Int (0 – 100 / null).
cold_water – cold water. (true, false).
hot_water – hot water. (true, false).
bathroom_light – lamp in bathroom. (true, false).
bathroom_presence – detector of presence in bathroom. (true, false).
bathroom_motion – detector of motion in bathroom. (true, false)
washing_machine – washing machine detector. string (“on”, “off”, “broken”).
leak_detector – detector of water leak (true, false).


# Reaction on events:
If there's leak (leak_detector=true), close cold (cold_water=false) and hot (hot_water=false) water and send email in moment of detecting.
If cold water is closed , immediately off boiler (boiler) and washing machibe (washing_machine) and don't turn on again, while cold water won't be open again
If boiler temperature (boiler_temperature) lower than hot_water_target_temperature - 10%, need to turn on boiler, and wait while she won't reach hot_water_target_temperature + 10%, after that boiler should be turned off
If curtains are sightly open (curtains == “slightly_open”), that means they on manual managing
If outdoor light lower than 50, open curtains, but only if bedroom_light don't turned on. If outdoor_light more than 50, ore bedroom_light turned on, curtains should be closed.
If smoke detector detected smoke  [air_conditioner, bedroom_light, bathroom_light, boiler, washing_machine] should be immediately turned off
If bedroom temperature is more than bedroom_target_temperature + 10% - turn on air_conditioner, and wait till temperature won't be lower than bedroom_target_temperature - 10%, after that conditioner should be turned off.

Checking of events is starting after sending form and described in file coursera_house/core/tasks.py


