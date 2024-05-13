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

#every undefined tag "!..." will raise an exception and notify the user
def construct_undefined(self, node):
    raise Exception("unknown tag: " + node.tag)    
