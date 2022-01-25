from ophyd import EpicsMotor, Device, Component as Cpt

class Stage(Device):
    x    = Cpt(EpicsMotor, '{UTS:1-Ax:X}Mtr')
    y    = Cpt(EpicsMotor, '{UTS:1-Ax:Y}Mtr')
    z    = Cpt(EpicsMotor, '{UTS:1-Ax:Z}Mtr')

S = Stage('XF:04BMC-ES:2', name='S')
S_x   = S.x
S_y   = S.y
S_z   = S.z

class MaiaStage(Device):
    x    = Cpt(EpicsMotor, '{PI180:1-Ax:MaiaX}Mtr')
    y    = Cpt(EpicsMotor, '{PI180:1-Ax:MaiaY}Mtr')
    z    = Cpt(EpicsMotor, '{PI180:1-Ax:MaiaZ}Mtr')
    r    = Cpt(EpicsMotor, '{SR50pp:1-Ax:MaiaR}Mtr')

M = MaiaStage('XF:04BMC-ES:2', name='M')
M_x   = M.x
M_y   = M.y
M_z   = M.z
M_r   = M.r
