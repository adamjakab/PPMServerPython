#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  License: MIT

import random
import string


def get_ugly_string(min_len, max_len, chars=None):
    rnd_len = random.randint(min_len, max_len)
    if not chars:
        chars = string.ascii_letters + string.digits
    else:
        if type(chars) is list:
            chars = "".join(chars)

    return ''.join(random.SystemRandom().choice(chars) for _ in range(rnd_len))
