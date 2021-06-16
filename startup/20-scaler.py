from ophyd import EpicsSignal
from ophyd.scaler import ScalerCH
from ophyd.device import (Component as C, DynamicDeviceComponent as DDC,
                          FormattedComponent as FC)
from ophyd.status import StatusBase


class ScalerMCA(Device):
    _default_read_attrs = ('channels', 'current_channel')
    _default_configuration_attrs = ('nuse', 'prescale')

    channels = DDC({f'mca{k:02d}': (EpicsSignal, f"mca{k}", {}) for k in range(1, 33)})
    startall = C(EpicsSignal, 'StartAll', string=True)
    stopall = C(EpicsSignal, 'StopAll', string=True)
    eraseall = C(EpicsSignal, 'EraseAll', string=True)
    erasestart = C(EpicsSignal, 'EraseStart', string=True)

    current_channel = C(EpicsSignal, 'CurrentChannel')
    nuse = C(EpicsSignal, 'NuseAll')
    prescale = C(EpicsSignal, 'Prescale')

    # high is acquiring
    status = C(EpicsSignal, 'Acquiring', string=True)

    def stage(self):
        super().stage()
        self.eraseall.put('Erase')

    def stop(self):
        self.stopall.put('Stop')

    def trigger(self):
        self.erasestart.put('Erase')

        return StatusBase()


class Scaler(Device):
    # MCAs
    mcas = C(ScalerMCA, '')
    # TODO maybe an issue with the timing around the triggering?
    cnts = C(ScalerCH, 'scaler1')

    def __init__(self, *args, mode='counting', **kwargs):
        super().__init__(*args, **kwargs)
        self.set_mode(mode)


    def match_names(self, N=20):
        self.cnts.match_names()
        for j in range(1, N+1):
            mca_ch = getattr(self.mcas.channels, f"mca{j:02d}")
            ct_ch = getattr(self.cnts.channels, f"chan{j:02d}")
            mca_ch.name = ct_ch.chname.get()

    # TODO put a soft signal around this so we can stage it
    def set_mode(self, mode):
        if mode == 'counting':
            self.read_attrs = ['cnts']
            self.configuration_attrs = ['cnts']
        elif mode == 'flying':
            self.read_attrs = ['mcas']
            self.configuration_attrs = ['mcas']
        else:
            raise ValueError

        self._mode = mode

    def trigger(self):
        if self._mode == 'counting':
            return self.cnts.trigger()
        elif mode == 'flying':
            return self.mcas.trigger()
        else:
            raise ValueError

    def stage(self):
        self.match_names()
        if self._mode == 'counting':
            return self.cnts.stage()
        elif mode == 'flying':
            return self.mcas.stage()
        else:
            raise ValueError

    def unstage(self):
        if self._mode == 'counting':
            return self.cnts.unstage()
        elif mode == 'flying':
            return self.mcas.unstage()
        else:
            raise ValueError

sclr1 = Scaler('XF:04BM-ES:2{Sclr:1}', name='sclr1')
sclr1.cnts.stage_sigs['count_mode'] = 'OneShot'
sclr1.cnts.channels.read_attrs = [f"chan{j:02d}" for j in range(1, 5)]
for j in [1, 3,]:
    getattr(sclr1.cnts.channels, f'chan{j:02d}').s.kind = 'normal'
sclr1.cnts.channels.chan02.s.kind = 'hinted'
sclr1.cnts.channels.chan04.s.kind = 'hinted'
sclr1.mcas.channels.read_attrs = [f"mca{j:02d}" for j in range(1, 5)]
sclr1.cnts.channels.configuration_attrs = [f"chan{j:02d}" for j in range(1, 5)]
sclr1.mcas.channels.configuration_attrs = [f"mca{j:02d}" for j in range(1, 5)]
sclr1.match_names(32)
sclr1.set_mode('counting')
