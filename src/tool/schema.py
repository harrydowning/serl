from typing import Tuple
import tool.utils as utils
import jsonschema

meta = {
    'type': 'object',
    'properties': {
        'tokens': {
            'type': 'object',
            'properties': {
                'ref': {
                    'type': ['string', 'boolean']
                },
                'regex': {
                    'type': 'boolean'
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
            'type': 'object',
            'patternProperties': {
                '^.*$': {'type': 'string'} # TODO depends
            },
        },
        'commands': {
            'type': 'object',
            'patternProperties': {
                '^.*$': {'type': 'string'} # TODO depends
            },
        },
        'requirements': {
            'type': 'string'
        }
    },
    'anyOf': [
        {'required': ['tokens', 'grammar', 'code']},
        {'required': ['tokens', 'grammar', 'commands']},
    ]
    
}

def validate(config: dict) -> Tuple[bool, str]:
    config = utils.recurse_tags(config, remove=True)
    try:
        jsonschema.validate(config, config_schema)
    except jsonschema.exceptions.ValidationError as ve:
        error = f'{ve.message} for key \'{".".join(ve.absolute_path)}\'.'
        return False, error
    return True, ''
