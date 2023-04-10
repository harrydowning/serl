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
                },
                'flags': {
                    'type': 'string'
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
        'tokentypes': { # TODO might rename
            'type': 'object',
            'patternProperties': {
                '^.*$': {
                    'type': 'string',
                }
            },
        },
        'styles': {
            'type': 'object',
            'patternProperties': {
                '^.*$': {
                    'type': 'string',
                }
            },
        },
        'environment': {
            'type': 'string'
        },
        'requirements': {
            'type': 'string'
        }
    },
    'required': ['grammar', 'code'] 
}

def validate(config: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(config_schema)
    errs = validator.iter_errors(config)
    return [f'{err.message} for \'{err.json_path}\'.' for err in errs]
