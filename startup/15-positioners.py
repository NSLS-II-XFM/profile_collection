from ophyd import EpicsMotor, Device, Component as Cpt


det1_x = EpicsMotor('XF:04BMC-ES{DET:1-Ax:X}Mtr', name='det1_x')

