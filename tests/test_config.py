import os

import serl.config as config

import pytest

@pytest.mark.parametrize('path, home, expected', [
    (['path', 'to', 'dir'], 'home', f'home{os.sep}.serl{os.sep}path{os.sep}to{os.sep}dir')
])
def test_get_config_dir(path, home, expected):
    tmp_expanduser = os.path.expanduser
    tmp_makedirs = os.makedirs
    
    os.path.expanduser = lambda x: home
    os.makedirs = lambda x, exist_ok: None
    actual = config.get_config_dir(path)
    assert actual == expected
    
    os.path.expanduser = tmp_expanduser
    os.makedirs = tmp_makedirs