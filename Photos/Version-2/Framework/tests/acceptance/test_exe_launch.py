"""
Acceptance tests — EXE launch smoke tests.

Launches HPM.exe as a subprocess and verifies it starts without immediately
crashing.  These tests are marked `slow` because they include deliberate
wait times and require the GUI subsystem.

Run selectively with::

    pytest tests/acceptance/test_exe_launch.py -m "acceptance and slow"
"""

import subprocess
import time

import pytest

from tests.acceptance.conftest import DIST_EXE


# How long (seconds) to wait before checking the process is still alive.
STARTUP_WAIT_SECONDS = 5


@pytest.fixture(scope="module")
def exe_process(exe_path):
    """
    Launch HPM.exe once for the module and terminate it after all tests.

    Uses scope='module' so the EXE is only launched once for the three
    tests below, reducing total wait time.
    """
    if not exe_path.exists():
        pytest.skip(f"HPM.exe not found at {exe_path} — build first")

    proc = subprocess.Popen(
        [str(exe_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Give the application time to initialise
    time.sleep(STARTUP_WAIT_SECONDS)

    yield proc

    # Teardown — terminate regardless of test outcomes
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.mark.acceptance
@pytest.mark.slow
class TestExeLaunch:
    """HPM.exe starts successfully and stays alive."""

    def test_exe_launches_without_crash(self, exe_process):
        """
        HPM.exe must still be running STARTUP_WAIT_SECONDS after launch.

        poll() returns None when the process is still alive.
        A non-None return code means the process has already exited,
        which indicates a crash or missing dependency.
        """
        assert exe_process.poll() is None, (
            f"HPM.exe exited with code {exe_process.poll()} within "
            f"{STARTUP_WAIT_SECONDS} seconds — possible crash or missing DLL"
        )

    def test_exe_has_valid_pid(self, exe_process):
        """The launched process has a valid positive PID."""
        assert exe_process.pid > 0, \
            "HPM.exe subprocess has no valid PID"

    def test_exe_terminates_cleanly(self, exe_process):
        """
        HPM.exe can be terminated via SIGTERM / process.terminate().

        This verifies the process is not in an unresponsive state and
        confirms our teardown won't leave zombie processes.
        """
        # Only run this if the process is still alive (prior tests may have
        # already caused it to exit)
        if exe_process.poll() is not None:
            pytest.skip("Process already exited before terminate test")

        exe_process.terminate()
        try:
            exe_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            exe_process.kill()
            pytest.fail("HPM.exe did not terminate within 10 seconds")

        # Any exit code is acceptable here — we just need it to stop
        assert exe_process.poll() is not None, \
            "HPM.exe is still running after terminate()"
