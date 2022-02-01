from nslsii.detectors.maia import MAIA

maia = MAIA('XFM:MAIA', name='maia')

import numpy as np

import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

sample_md = {"sample": {"name": "Ni mesh", "owner": "stolen"}}


def fly_maia(
    ystart,
    ystop,
    ynum,
    xstart,
    xstop,
    xnum,
    dwell,
    *,
    group=None,
    md=None,
    # shut_b,
    hf_stage,
    maia,
):
    """Run a flyscan with the maia


    Parameters
    ----------
    ystart, ystop : float
        The limits of the scan along the slow direction in absolute mm.

    ynum : int
        The number of pixels (rows) along the slow direction.

    xstart, xstop : float
        The limits of the scan along the fast direction in absolute mm.

    xnum : int
        The number of pixels (columns) along the fast direction.

    dwell : float
        The dwelll time in s.  This is used to set the motor velocity.

    group : str, optional
        The file group.  This goes into the file path that maia writes to.

    md : dict, optional
        Metadata to put into the start document.

        If there is a 'sample' key, then it must be a dictionary and the
        keys

           ['info', 'name', 'owner', 'serial', 'type']

        are passed through to the maia metadata.

        If there is a 'scan' key, then it must be a dictionary and the
        keys

             ['region', 'info', 'seq_num', 'seq_total']

        are passed through to maia metadata.
    """
    # shutter = shut_b
    md = md or {}
    _md = {
        "detectors": ["maia"],
        "shape": [ynum, xnum],
        "motors": [m.name for m in [hf_stage.y, hf_stage.x]],
        "num_steps": xnum * ynum,
        "plan_args": dict(
            ystart=ystart,
            ystop=ystop,
            ynum=ynum,
            xstart=xstart,
            xstop=xstop,
            xnum=xnum,
            dwell=dwell,
            group=repr(group),
            md=md,
        ),
        "extents": [[ystart, ystop], [xstart, xstop]],
        "snaking": [False, True],
        "plan_name": "fly_maia",
    }
    _md.update(md)

    md = _md

    sample_md = md.get("sample", {})
    for k in ["info", "name", "owner", "serial", "type"]:
        v = sample_md.get(k, "")
        sig = getattr(maia, "meta_val_sample_{}_sp.value".format(k))
        yield from bps.mv(sig, str(v))

    scan_md = md.get("scan", {})
    for k in ["region", "info", "seq_num", "seq_total"]:
        v = scan_md.get(k, "")
        sig = getattr(maia, "meta_val_scan_{}_sp.value".format(k))
        yield from bps.mv(sig, str(v))

    if group is not None:
        yield from bps.mv(maia.blog_group_next_sp.value, group)

    if xstart > xstop:
        xstop, xstart = xstart, xstop

    if ystart > ystop:
        ystop, ystart = ystart, ystop

    # Pitch must match what raster driver uses for pitch ...
    x_pitch = abs(xstop - xstart) / (xnum - 1)
    y_pitch = abs(ystop - ystart) / (ynum - 1)

    # TODO compute this based on someting
    spd_x = x_pitch / dwell

    yield from bps.mv(hf_stage.x, xstart, hf_stage.y, ystart)

    x_val = yield from bps.rd(hf_stage.x)
    y_val = yield from bps.rd(hf_stage.y)
    # TODO, depends on actual device
    yield from bps.mv(maia.enc_axis_0_pos_sp.value, x_val)
    yield from bps.mv(maia.enc_axis_1_pos_sp.value, y_val)

    yield from bps.mv(maia.x_pixel_dim_origin_sp.value, xstart)
    yield from bps.mv(maia.y_pixel_dim_origin_sp.value, ystart)

    yield from bps.mv(maia.x_pixel_dim_pitch_sp.value, x_pitch)
    yield from bps.mv(maia.y_pixel_dim_pitch_sp.value, y_pitch)

    yield from bps.mv(maia.x_pixel_dim_coord_extent_sp.value, xnum)
    yield from bps.mv(maia.y_pixel_dim_coord_extent_sp.value, ynum)
    yield from bps.mv(maia.scan_order_sp.value, "01")
    yield from bps.mv(maia.meta_val_scan_order_sp.value, "01")
    yield from bps.mv(maia.pixel_dwell.value, dwell)
    yield from bps.mv(maia.meta_val_scan_dwell.value, str(dwell))

    yield from bps.mv(maia.meta_val_beam_particle_sp.value, "photon")
    yield from bps.mv(
        maia.meta_val_beam_energy_sp.value, "{:.2f}".format(20_000)
        )
    #    yield from bps.mv(maia.maia_scan_info
    # need something to generate a filename here.
    #    yield from bps.mv(maia.blog_group_next_sp,datafile))
    # start blog in kickoff?

    @bpp.reset_positions_decorator([hf_stage.x.velocity])
    def _raster_plan():

        # set the motors to the right speed
        yield from bps.mv(hf_stage.x.velocity, spd_x)

        # yield from bps.mv(shutter, "Open")
        start_uid = yield from bps.open_run(md)

        yield from bps.mv(maia.meta_val_scan_crossref_sp.value, start_uid)
        # long int here.  consequneces of changing?
        #    yield from bps.mv(maia.scan_number_sp,start_uid)
        yield from bps.stage(maia)  # currently a no-op

        yield from bps.kickoff(maia, wait=True)
        yield from bps.checkpoint()
        # by row
        for i, y_pos in enumerate(np.linspace(ystart, ystop, ynum)):
            yield from bps.checkpoint()
            #yield from bps.sleep(0.05)
            # move to the row we want
            yield from bps.mv(hf_stage.y, y_pos, wait=True)
            if i % 2:
                # for odd-rows move from start to stop
                yield from bps.mv(hf_stage.x, xstop, wait=True)
            else:
                # for even-rows move from stop to start
                yield from bps.mv(hf_stage.x, xstart, wait=True)
            #yield from bps.sleep(0.02)

    def _cleanup_plan():
        # stop the maia ("I'll wait until you're done")
        yield from bps.complete(maia, wait=True)
        # shut the shutter
        # yield from bps.mv(shutter, "Close")
        # collect data from maia
        yield from bps.collect(maia)

        yield from bps.unstage(maia)
        yield from bps.close_run()
        yield from bps.mv(maia.meta_val_scan_crossref_sp.value, "")
        for k in ["info", "name", "owner", "serial", "type"]:
            sig = getattr(maia, "meta_val_sample_{}_sp.value".format(k))
            yield from bps.mv(sig, "")

        for k in ["region", "info", "seq_num", "seq_total"]:
            sig = getattr(maia, "meta_val_scan_{}_sp.value".format(k))
            yield from bps.mv(sig, "")
        yield from bps.mv(maia.meta_val_beam_energy_sp.value, "")
        yield from bps.mv(maia.meta_val_scan_dwell.value, "")
        yield from bps.mv(maia.meta_val_scan_order_sp.value, "")

    return (yield from bpp.finalize_wrapper(_raster_plan(), _cleanup_plan()))


def fly_maia_finger_sync(
    ystart,
    ystop,
    ynum,
    xstart,
    xstop,
    xnum,
    dwell,
    *,
    group=None,
    md=None,
    shut_b,
    hf_stage,
):
    shutter = shut_b
    md = md or {}
    _md = {
        "detectors": ["maia"],
        "shape": [ynum, xnum],
        "motors": [m.name for m in [hf_stage.y, hf_stage.x]],
        "num_steps": xnum * ynum,
        "plan_args": dict(
            ystart=ystart,
            ystop=ystop,
            ynum=ynum,
            xstart=xstart,
            xstop=xstop,
            xnum=xnum,
            dwell=dwell,
            group=repr(group),
            md=md,
        ),
        "extents": [[ystart, ystop], [xstart, xstop]],
        "snaking": [False, True],
        "plan_name": "fly_maia",
    }
    _md.update(md)

    md = _md

    if xstart > xstop:
        xstop, xstart = xstart, xstop

    if ystart > ystop:
        ystop, ystart = ystart, ystop

    # Pitch must match what raster driver uses for pitch ...
    x_pitch = abs(xstop - xstart) / (xnum - 1)

    # TODO compute this based on someting
    spd_x = x_pitch / dwell

    yield from bps.mv(hf_stage.x, xstart, hf_stage.y, ystart)

    @bpp.reset_positions_decorator([hf_stage.x.velocity])
    def _raster_plan():

        # set the motors to the right speed
        yield from bps.mv(hf_stage.x.velocity, spd_x)

        yield from bps.mv(shutter, "Open")
        yield from bps.open_run(md)

        yield from bps.checkpoint()
        # by row
        for i, y_pos in enumerate(np.linspace(ystart, ystop, ynum)):
            yield from bps.checkpoint()
            # move to the row we want
            yield from bps.mv(hf_stage.y, y_pos)
            if i % 2:
                # for odd-rows move from start to stop
                yield from bps.mv(hf_stage.x, xstop)
            else:
                # for even-rows move from stop to start
                yield from bps.mv(hf_stage.x, xstart)

    def _cleanup_plan():
        # shut the shutter
        yield from bps.mv(shutter, "Close")

        yield from bps.close_run()

    return (yield from bpp.finalize_wrapper(_raster_plan(), _cleanup_plan()))
