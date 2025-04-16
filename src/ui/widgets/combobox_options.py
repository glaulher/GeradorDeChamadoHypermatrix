import json
from utils.resource import externalPath

def load_combobox_options(combo, key):
  with open(externalPath('data/combobox_options.json'), 'r', encoding='utf-8') as file:
    options = json.load(file)
  combo.addItems(options.get(key, []))