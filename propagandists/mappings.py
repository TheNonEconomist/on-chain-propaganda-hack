# TODO: TO be replaced by a robust tool that does
# 1) Grabs materials and stores in a DB identifiable per community ,situation, and emotion
# 2) AI contextual awareness capability that reads sentiment and does mapping from query to generation appropriately
# 3) 

import os 
import json


MATERIAL_PATH = os.getenv('MATERIAL_PATH')

def random_mapping():
    with open(MATERIAL_PATH + "random.json", "r") as f:
        materials = json.load(f)

def educational_mapping(emotion, situation):
    with open(MATERIAL_PATH + "educational.json", "r") as f:
        materials = json.load(f)
    