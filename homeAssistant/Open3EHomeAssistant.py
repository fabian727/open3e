import json
import time
import yaml

from dataclasses import dataclass

#while loading the yaml, there might be "tags" (e.g. "!secret"), which trigger python to do something
#this can be overloaded, which is implemented in the following lines
@dataclass
class secret:
    string: str

#overload the yaml loader with this one, to allow the callbacks
class overloader(yaml.SafeLoader):
    pass

#if the tag "!secret" is found, this callback shall handle it
def construct_secret(self, node):
    if node.value == "vitocal_sn":
        #TODO: return the real serial number (if available)
        return "unknown_serial"
    else:
        raise Exception("unknown secret value: " + node.value)

#every undefined tag "!..." will raise an exception and notify the user
def construct_undefined(self, node):
    raise Exception("unknown tag: " + node.tag)    

#yet unused
def discover(mqtt_client):
    file=open("HomeAssistantDatapoints.json")
    text=file.read()
    allDevices=json.load(text, Loader=overloader)

    #TODO: currently hard coded, could be set via json?
    deviceName="Viessmann Heatpump"
    canBaseId="680"

    #TODO: V is just for Viessman to make it more unique within HomeAssistant; could also be O3E but i don't like the O or is it 0?
    deviceIdentifier="V"+canBaseId
    for attribute, entity in allDevices.items():
        #is it a real entry or "just" versioning (last entry within json)
        if attribute != "Version":
            entityConfig={
            "name":entity["id"],
            #TODO: this state topic is currently hard coded to fit an "mfstr" of "{ecuAddr:03X}/{didName}"
            "state_topic":"open3e/"+canBaseId+"/"+entity["id"],
            "command_topic": "open3e/cmnd",
            "unique_id":deviceIdentifier+"_"+entity["id"],
            "device":{
                "identifiers":[
                    deviceIdentifier
                ],
                "name":deviceName
            }
            }
            if "icon" in entity:
                icon = {"icon":entity["icon"]}
                entityConfig.update(icon)
            if "device_class" in entity:
                device_class = {"device_class":entity["device_class"]}
                entityConfig.update(device_class)
            if "unit_of_measurement" in entity:
                unit = {"unit_of_measurement":entity["unit_of_measurement"]}
                entityConfig.update(unit)

            print(entityConfig)
            #TODO only sensor is currently supported!, but there is also:  button, camera, cover, number, select and I guess more (add to json?)
            deviceType = "sensor"
            #TODO the mqtt string is hard styled!, make it adapting to "mqttformatstring"
            topic="homeassistant/"+deviceType+"/"+deviceIdentifier+"/"+deviceIdentifier+"_"+deviceType+"_"+entity["id"]+"/config"
            mqtt_client.publish(topic, json.dumps(entityConfig), retain=True)
    time.sleep(3)

#copy and paste the vitocal250.yaml to mqtt
def copypaste(mqtt_client):
    overloader.add_constructor('!secret', construct_secret)
    overloader.add_constructor(None, construct_undefined)
    #import yaml

    with open('homeAssistant/vitocal250.yaml', 'r') as file:
        entities = yaml.load(file, Loader=overloader)
        #hass_type e.g. number, climate, ...
    for hass_type in entities["mqtt"]:
        for entity in entities["mqtt"][hass_type]:
            if "state_topic" in entity:
                state_topic = entity["state_topic"]
            elif "mode_state_topic" in entity:
                state_topic = entity["mode_state_topic"]
            #TODO: currently beleiving that the state topic will start with "open3e/", which shall be skipped
            state_topic = state_topic[:8] + state_topic.replace('/','_')[8:]
            print(state_topic)
            #TODO: the yaml is already existing within hass, therefore the unique ids are already in usage
            if "unique_id" in entity:
                entity["unique_id"] = "auto_" + entity["unique_id"]
            if "object_id" in entity:
                entity["object_id"] = "auto_" + entity["object_id"]

            topic="homeassistant/"+hass_type+"/"+state_topic+"/config"
            ret = mqtt_client.publish(topic, json.dumps(entity), retain=True)
            #mqtt_client.publish(topic, yaml.dump(entity), retain=True)
            #doing so to make it retained within MQTT Explorer
            #mqtt_client.subscribe(topic)
    #wait some seconds, so subscription can be finished
    time.sleep(3)
