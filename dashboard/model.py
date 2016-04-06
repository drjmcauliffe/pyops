from wtforms import Form, FloatField, validators
from math import pi

class InputForm(Form):
    """Summary

    Attributes:
        A (TYPE): Description
        b (TYPE): Description
        w (TYPE): Description
    """
    A = FloatField(
        label='amplitude (m)', default=1.0,
        validators=[validators.InputRequired()])
    b = FloatField(
        label='damping factor (kg/s)', default=0,
        validators=[validators.InputRequired()])
    w = FloatField(
        label='frequence (1/s)', default=2*pi,
        validators=[validators.InputRequired()])
    T = FloatField(
        label='time interval (s)', default=18,
        validators=[validators.InputRequired()])