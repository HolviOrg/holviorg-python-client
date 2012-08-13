# -*- coding: utf-8 -*-
from .exceptions import HolviCryptException

ENC_NONE = "ENC:NONE"
ENC_AES256 = "ENC:AES256"
IV_DEFAULT = "1234567890123456"
SERVER_DEFAULT = "https://my.holvi.org/"

def validate_encryption_mode(level, throw_exception=True):
    if level in [ENC_NONE, ENC_AES256]:
        return True
    if throw_exception:
        raise HolviCryptException(901, 'Invalid encryption mode')
    return False
