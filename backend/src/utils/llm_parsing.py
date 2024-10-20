import json


def extract_and_parse_json(input_string):
    try:
        input_string = input_string.replace("“", '"').replace("”", '"')
        start_idx = input_string.find("{")
        end_idx = input_string.find("}", start_idx)
        json_str = input_string[start_idx : end_idx + 1]
        json_obj = json.loads(json_str)
        return json_obj
    except Exception as e:
        return None
