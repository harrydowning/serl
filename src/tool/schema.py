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

def validate(config: dict) -> bool:
    try:
        jsonschema.validate(config, config_schema)
    except jsonschema.exceptions.ValidationError:
        return False
    return True
