from ophyd import EpicsMotor, Device, Component as Cpt

class Stage(Device):
    x    = Cpt(EpicsMotor, '{UTS:1-Ax:X}Mtr')
    y    = Cpt(EpicsMotor, '{UTS:1-Ax:Y}Mtr')
    z    = Cpt(EpicsMotor, '{UTS:1-Ax:Z}Mtr')

S = Stage('XF:04BMC-ES:2', name='S')
S_x   = S.x
S_y   = S.y
S_z   = S.z
