# Deployment acceptance tests
# Running the tests from IPython
# %run -i ~/.ipython/profile_collection/acceptance_tests/test_step_scans.py


def test_fly_maia():
    """
    Fly scan test 1.
    Before running this test it is nessecary to check with the beamline that it is safe to execute.
    If db.table() and export scan complete without errors than it was successful.
    """

    input("Press any key to confirm that it is safe to execute this plan.")

    print("Starting fly scan test 1")

    (uid,) = RE(
        fly_maia(
            ystart=130.0,
            ystop=130.02,
            ynum=2,
            xstart=60.0,
            xstop=60.1,
            xnum=10,
            dwell=0.1,
            hf_stage=M,
            maia=maia,
        )
    )

    print("Fly scan complete")
    print("Reading scan from databroker")
    db[uid].table(fill=True)
    print("Test 1 is complete")


def test_step2d():
    """
    Step scan test 1.
    Before running this test it is nessecary to check with the beamline that it is safe to execute.
    If db.table() and export scan complete without errors than it was successful.
    """

    input("Press any key to confirm that it is safe to execute this plan.")

    print("Starting step scan test 1")
    (uid,) = RE(
        step2d(
            ystart=-5.02,
            ystop=-5.0,
            ysteps=2,
            xstart=-17.1,
            xstop=-17.0,
            xsteps=10,
            count_time=1.0,
            snake=False,
            x3m=True,
        )
    )

    print("Test 2 complete")
    print("Reading scan from databroker")
    db[uid].table(fill=True)
