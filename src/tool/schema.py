from typing import Tuple
import jsonschema

meta = {
    'type': 'object',
    'properties': {
        'tokens': {
            'type': 'object',
            'properties': {
                'ref': {
                    'type': ['string', 'boolean']
                }
            }
        }
    }
}

config_schema = {
    'type': 'object',
    'properties': {
        'meta': meta,
        'version': {
            'type': ['string', 'number']
        },
        'usage': {
            'type': 'string'
        },
        'tokens': {
            'type': 'object',
            'properties': {
                '_ignore': {
                    'type': 'string'
                }
            },
            'patternProperties': {
                '^.*$': {
                    'type': 'string',
                }
            },
        },
        'precedence': {
            'type': 'array',
            'items': {
                'type': 'string'
            }
        },
        'constructors': {
            'type': 'object'
        },
        'grammar': {
            'type': 'object',
            'patternProperties': {
                '^.*$': {
                    'type': ['string', 'array'],
                    'items': {
                        'type': 'string'
                    }
                }
            },
        },
        'code': {
            'type': 'object'
        },
        'requirements': {
            'type': 'string'
        }
    },
    'required': ['tokens', 'grammar', 'code']
}

def remove_tags(obj):
    if type(obj) == dict:
        return {k: remove_tags(v) for k, v in obj.items()}
    elif type(obj) == list:
        return [remove_tags(v) for v in obj]
    elif type(obj) == tuple and len(obj) == 2:
        return obj[1]
    else:
        return obj    

def validate(config: dict) -> Tuple[bool, str]:
    config = remove_tags(config)
    try:
        jsonschema.validate(config, config_schema)
    except jsonschema.exceptions.ValidationError as ve:
        error = f'{ve.message} for key \'{".".join(ve.absolute_path)}\'.'
        return False, error
    return True, ''
