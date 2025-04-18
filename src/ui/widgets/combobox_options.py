import json

from utils.resource import external_path


def load_combobox_options(combo, key):
    with open(
        external_path("data/combobox_options.json"), "r", encoding="utf-8"
    ) as file:
        options = json.load(file)
    combo.addItems(options.get(key, []))
