from typing import Tuple
import jsonschema

meta = {
    "type": "object",
    "properties": {
        "token-ref": {
            "type": "object",
            "properties": {
                "start": {
                    "type": "string"
                },
                "end": {
                    "type": "string"
                }
            }
        }
    }
}

config_schema = {
    "type": "object",
    "properties": {
        "meta": meta,
        "version": {
            "type": ["string", "number"]
        },
        "usage": {
            "type": "string"
        },
        "tokens": {
            "type": "object",
            "properties": {
                "_ignore": {
                    "type": "string"
                }
            }
        },
        "grammar": {
            "type": "object"
        },
        "code": {
            "type": "object"
        },
        "requirements": {
            "type": "string"
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
