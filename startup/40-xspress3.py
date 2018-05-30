from ophyd.areadetector import (AreaDetector, PixiradDetectorCam, ImagePlugin,
                                TIFFPlugin, StatsPlugin, HDF5Plugin,
                                ProcessPlugin, ROIPlugin, TransformPlugin,
                                OverlayPlugin)
from ophyd.areadetector.plugins import PluginBase
from ophyd.areadetector.cam import AreaDetectorCam
from ophyd.device import BlueskyInterface
from ophyd.areadetector.trigger_mixins import SingleTrigger
from ophyd.areadetector.filestore_mixins import (FileStoreIterativeWrite,
                                                 FileStoreHDF5IterativeWrite,
                                                 FileStoreTIFFSquashing,
                                                 FileStoreTIFF)
from ophyd import Signal
from ophyd import Component as C

from hxntools.handlers import register
register(db)

from pathlib import PurePath
from hxntools.detectors.xspress3 import (XspressTrigger, Xspress3Detector,
                                         Xspress3Channel, Xspress3FileStore, logger)
from databroker.assets.handlers import Xspress3HDF5Handler, HandlerBase


class SrxXspress3Detector(XspressTrigger, Xspress3Detector):
    roi_data = Cpt(PluginBase, 'ROIDATA:')
    channel1 = C(Xspress3Channel, 'C1_', channel_num=1, read_attrs=['rois'])
    channel2 = C(Xspress3Channel, 'C2_', channel_num=2, read_attrs=['rois'])
    channel3 = C(Xspress3Channel, 'C3_', channel_num=3, read_attrs=['rois'])
    channel4 = C(Xspress3Channel, 'C4_', channel_num=4, read_attrs=['rois'])
    # create_dir = Cpt(EpicsSignal, 'HDF5:FileCreateDir')

    hdf5 = Cpt(Xspress3FileStore, 'HDF5:',
               read_path_template='/mnt/xspress3/data-srv2/x3mini-test/',
               write_path_template='/home/xspress3/data-srv2/x3mini-test/',
               root='/mnt/xspress3/data-srv2/',
               reg=db.reg,
               )

    def __init__(self, prefix, *, configuration_attrs=None, read_attrs=None,
                 **kwargs):
        if configuration_attrs is None:
            configuration_attrs = ['external_trig', 'total_points',
                                   'spectra_per_point', 'settings',
                                   'rewindable']
        if read_attrs is None:
            read_attrs = ['channel1', 'channel2', 'channel3', 'channel4', 'hdf5']
        super().__init__(prefix, configuration_attrs=configuration_attrs,
                         read_attrs=read_attrs, **kwargs)
        # self.create_dir.put(-3)

    def stop(self):
        ret = super.stop()
        self.hdf5.stop()
        return ret

    def stage(self):
        ret = super().stage()
        self.hdf5._resource_uid = self.hdf5._resource
        return ret

    # Currently only using three channels. Uncomment these to enable more
    # channels:
    # channel5 = C(Xspress3Channel, 'C5_', channel_num=5)
    # channel6 = C(Xspress3Channel, 'C6_', channel_num=6)
    # channel7 = C(Xspress3Channel, 'C7_', channel_num=7)
    # channel8 = C(Xspress3Channel, 'C8_', channel_num=8)


xs = SrxXspress3Detector('XSPRESS3-EXAMPLE:', name='xs')
for n in [1, 2, 3, 4]:
    getattr(xs, f'channel{n}').rois.read_attrs = ['roi{:02}'.format(j) for j in [1, 2, 3, 4]]
xs.hdf5.num_extra_dims.put(0)
xs.channel2.vis_enabled.put(1)
xs.channel3.vis_enabled.put(1)
xs.settings.num_channels.put(4)

# This is necessary for when the ioc restarts
# we have to trigger one image for the hdf5 plugin to work correclty
# else, we get file writing errors
# xs.hdf5.warmup()

# Hints:
for n in [1, 2]:
    getattr(xs, f'channel{n}').rois.roi01.value.kind = 'hinted'

