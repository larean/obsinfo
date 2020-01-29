#!/usr/bin/env python3
import python_jsonschema_objects as pjs
import json

schema_file='network.schema.json'
with open(schema_file,'r') as f:
    schema=json.load(f)
builder = pjs.ObjectBuilder(schema)
ns = builder.build_classes()