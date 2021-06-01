"""
The MIT License (MIT)

Copyright (c) 2014 - 2016 Mohab Usama
"""


class GuacamoleError(Exception):
    def __init__(self, message):
        super(GuacamoleError, self).__init__(
            'Guacamole Protocol Error. {}'.format(message)
        )


class InvalidInstruction(Exception):
    def __init__(self, message):
        super(InvalidInstruction, self).__init__(
            'Invalid Guacamole Instruction! {}'.format(message)
        )
