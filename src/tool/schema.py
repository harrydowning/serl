from typing import Tuple
import jsonschema

meta = {
    'type': 'object',
    'properties': {
        'ref': {
            'type': ['object', 'boolean'],
            'properties': {
                'start': {
                    'type': 'string'
                },
                'end': {
                    'type': 'string'
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

def validate(config: dict) -> Tuple[bool, str]:
    try:
        jsonschema.validate(config, config_schema)
    except jsonschema.exceptions.ValidationError as ve:
        error = f'{ve.message} for key \'{".".join(ve.absolute_path)}\'.'
        return False, error
    return True, ''
