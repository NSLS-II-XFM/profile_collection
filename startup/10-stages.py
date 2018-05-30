from ophyd import EpicsMotor, Device, Component as Cpt

# TODO this need to be made xps aware classes
class Stage(Device):
    x = Cpt(EpicsMotor, 'm1')
    y = Cpt(EpicsMotor, 'm2')
    z = Cpt(EpicsMotor, 'm3')
        
S = Stage('XF:04BM-ES:2:', name='S')
S_x = S.x
S_y = S.y
S_z = S.z

