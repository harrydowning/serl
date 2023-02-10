from typing import Tuple
import jsonschema

config_schema = {
    "type": "object",
    "properties": {
        "version": {
            "type": ["string", "number"]
        },
        "usage": {
            "type": "string"
        },
        "tokens": {
            "type": "object"
        },
        "grammar": {
            "type": "object"
        },
        "code": {
            "type": "object"
        }
    },
    "required": ["tokens", "grammar", "code"]
}

def validate(config: dict) -> Tuple[bool, str]:
    try:
        jsonschema.validate(config, config_schema)
    except jsonschema.exceptions.ValidationError as ve:
        return False, ve.message
    return True, ''
