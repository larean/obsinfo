"""
The following shows that jsofref crushes everthing else on the same level

>>> json_str = '{"A": {"C": 2}, "B": {"$ref": "#/A", "D": "howdy"}}'
>>> data = jsonref.loads(json_str)
>>> data == {'A': {'C': 2}, 'B': {'C': 2}}
"""
import jsonref
from pprint import pprint

json_str = """{"A": {"C": 2}, "B": {"$ref": "#/A", "D": "howdy"}}"""
json_str = """{"A": 2, "B": {"$ref": "#/A", "D": "howdy"}}"""
#json_str = """{"real": [1, 2, 3, 4], "ref": {"$ref": "#/real"}}"""
data = jsonref.loads(json_str)
pprint(data)