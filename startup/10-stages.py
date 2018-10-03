from ophyd import EpicsMotor, Device, Component as Cpt

# TODO this need to be made xps aware classes
class Stage(Device):
    x    = Cpt(EpicsMotor, '2:m1')
    y    = Cpt(EpicsMotor, '2:m2')
    z    = Cpt(EpicsMotor, '2:m3')

S = Stage('XF:04BM-ES:', name='S')
S_x   = S.x
S_y   = S.y
S_z   = S.z
