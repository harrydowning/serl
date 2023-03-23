from typing import Tuple
import jsonschema

meta = {
    'type': 'object',
    'properties': {
        'tokens': {
            'type': 'object',
            'properties': {
                'ref': {
                    'type': ['string', 'null']
                },
                'regex': {
                    'type': 'boolean'
                },
                'ignore': {
                    'type': ['string', 'null']
                }
            }
        },
        'grammar': {
            'type': 'object',
            'properties': {
                'permissive': {
                    'type': 'boolean'
                }
            }
        },
        'commands': {
            'type': 'object',
            'properties': {
                'prefix': {
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
        'sync': {
            'type': 'string'
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
                '^.*$': {
                    'type': ['string', 'array'],
                    'items': {
                        'type': ['string', 'null']
                    }
                }
            },
        },
        'commands': {
            'type': 'object',
            'patternProperties': {
                '^.*$': {
                    'type': ['string', 'array'],
                    'items': {
                        'type': ['string', 'null']
                    }
                }
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
    try:
        jsonschema.validate(config, config_schema)
    except jsonschema.exceptions.ValidationError as ve:
        error = f'{ve.message} for key \'{".".join(ve.absolute_path)}\'.'
        return False, error
    return True, ''
