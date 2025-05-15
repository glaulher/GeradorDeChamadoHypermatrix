import inspect
import json

import pyperclip


def payload_and_output(payload_dict: dict, output_file: str = "payload.json") -> str:
    caller_filename = inspect.stack()[1].filename

    if "control_pim_window.py" in caller_filename:
        # Sanitiza os dados
        for k in payload_dict:
            payload_dict[k] = (
                str(payload_dict[k])
                .replace("\r", "")
                .replace("\n", "")
                .replace("\t", "")
                .strip()
            )
    else:
        for k in payload_dict:
            payload_dict[k] = str(payload_dict[k]).replace("\t", "").strip()

    # Salva o JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload_dict, f, ensure_ascii=False, indent=4)

    output_str = ""
    for key in payload_dict:
        if key == "Assunto":
            output_str += f"*{payload_dict[key]}*\n\n"
        else:
            output_str += f"*{key}*: {payload_dict[key]}\n"

    if "control_pim_window.py" in caller_filename:
        pyperclip.copy("\t".join(v for k, v in payload_dict.items() if k != "Assunto"))
    else:
        pyperclip.copy(output_str)

    return output_str
