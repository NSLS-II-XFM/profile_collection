def set_count_time(secs):
    return (yield from bps.mov(
        sclr1.cnts.preset_time, secs,
        xs.settings.acquire_time, secs,
#        pe1.cam.acquire_time, secs,
    ))


def xfmcount(num, count_time, *, x3m=True, **kwargs):
#def xfmcount(num, count_time, *, xrd=False, x3m=True, **kwargs):
    """Count the detectors

    Parameters
    ----------
    num : int
        The number of exposures to take

    count_time : float
        Exposure time in seconds.

    xrd : bool, optional
        If the XRD (PE) detector should be used

        keyword only, defaults to False

    x3m : bool, optional
        If the xspress3 mini detector should be used

        keyword only, defaults to True

    **kwargs
       passed through to bp.count

    """
    dets = [sclr1]
#    if xrd:
#        dets.append(pe1)

    if x3m:
        dets.append(xs)
        if num is None:
            raise TypeError("can not count forever with x3m")
        yield from bps.mov(xs.total_points, num)

    yield from set_count_time(count_time)

    yield from bp.count(dets, num, **kwargs)


    """test
    This a 2D step scan for centering a DAC

@bpp.reset_positions_decorator(devices=[DAC.x, DAC.y])
def DAC_centering(ystart, ystop, ysteps,
                  xstart, xstop, xsteps,
                  count_time,
                  snake=True):

    dets = [sclr1]

#    yield from bp.grid_scan(dets,
#                            DACy, ystart, ystop, ysteps,
#                            DACx, xstart, xstop, xsteps,
#                            snake)

    yield from bp.spiral(dets,
                         DACx, DACy,
                         x_start=14.00, y_start=78.00,
                         x_range=0.15, y_range=0.15,
                         dr=0.15, nth=300)
    """


@bpp.reset_positions_decorator(devices=[S.x, S.y])
def step2d(ystart, ystop, ysteps,
           xstart, xstop, xsteps,
           count_time,
           snake=True, *,
           x3m=True,
           **kwargs):
    """
    This a 2D step scan

    Parameters
    ----------
    ystart, ystop : float
        Absolute start and stop position of Y stage

    ystep : int
        Number of positions in Y

    xstart, xstop : float
        Absolute start and stop position of X stage

    xstep : int
        Number of positions in X

    count_time : float
        Exposure time in seconds.

    snake : bool, optional
        raster scan without return

    xrd : bool, optional
        If the XRD (PE) detector should be used

        keyword only, defaults to False

     x3m : bool, optional
        If the xspress3 mini detector should be used

        keyword only, defaults to True

    **kwargs
       passed through to bp.grid_scan


    """
    dets = [sclr1]
#    if xrd:
#        dets.append(pe1)


    if x3m:
        dets.append(xs)
        yield from bps.mov(xs.total_points, xsteps*ysteps)

    yield from set_count_time(count_time)
    yield from bp.grid_scan(dets,
                            S.y, ystart, ystop, ysteps,
                            S.x, xstart, xstop, xsteps,
                            snake, **kwargs)
