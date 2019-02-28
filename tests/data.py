import json
import os


BLOCKS_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "data", "blocks.json")


with open(BLOCKS_PATH, "r") as f:
    BLOCKS = json.loads(f.read())["blocks"]
