from ophyd import EpicsMotor

DACx = EpicsMotor('XF:04BMC-ES{DET:1-Ax:Z}Mtr', name='DAC X')
DACy = EpicsMotor('XF:04BMC-ES{DET:1-Ax:Y}Mtr', name='DAC Y')
DACz = EpicsMotor('XF:04BM-ES:1:m7',            name='DAC Z')
