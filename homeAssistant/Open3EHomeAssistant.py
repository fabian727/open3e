import json
import time
import yaml
from homeAssistant.yamlOverloader import overloader
from homeAssistant.yamlOverloader import construct_undefined

_serial = "unknown_serial"

#if the tag "!secret" is found, this callback shall handle it
def construct_secret(self, node):
    if node.value == "vitocal_sn":
        #TODO: return the real serial number (if available)
        return _serial
    else:
        raise Exception("unknown secret value: " + node.value)

class detection:
    def __init__(self):
        self.cmndTopic = ""
        #_serial is already preset with a default

    def setCmndTopic(self, topic):
        self.cmndTopic = topic
    def setSerial(self, serial):
        _serial = serial

    #copy and paste the vitocal250.yaml to mqtt
    #but only the datapoints, which were found
    def copypaste(self, mqtt_client):
        overloader.add_constructor('!secret', construct_secret)
        overloader.add_constructor(None, construct_undefined)
        #import yaml

        with open('homeAssistant/vitocal250.yaml', 'r') as file:
            entities = yaml.load(file, Loader=overloader)
            #hass_type e.g. number, climate, ...
        for hassType in entities["mqtt"]:
            for entity in entities["mqtt"][hassType]:
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
                if self.cmndTopic == "":
                    if "command_topic" in entity:
                        entity.pop("command_topic")
                    if "command_template" in entity:
                        entity.pop("command_template")
                else:
                    entity["command_topic"] = self.cmndTopic
                topic="homeassistant/"+hassType+"/"+state_topic+"/config"
                ret = mqtt_client.publish(topic, json.dumps(entity), retain=True)
