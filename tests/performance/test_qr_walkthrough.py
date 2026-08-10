import logging
import pytest

from ems_opg.core.paths_manager import PathManager
from ems_opg.services.qr_service import QRService

paths = PathManager()
paths.create_directories()

LOG_FILE = paths.logs_dir / "qr_testing_test.log"

logger = logging.getLogger("qr_testing_test")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers when pytest reloads modules
if not logger.handlers:

    file_handler = logging.FileHandler(LOG_FILE, mode="w")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

@pytest.fixture(scope="module")
def qr_service():
    """
    Creates one QRService for the entire test module.
    QR images are written into cache/qr.
    """

    return QRService(
        output_directory=paths.qr_cache
    )


def assert_generated_qr(result, expected_name, expected_fragments):
    assert result.path.exists()
    assert result.path.suffix == ".png"
    assert result.filename == f"{expected_name}.png"
    assert result.path.name == f"{expected_name}.png"
    assert result.path.parent == paths.qr_cache

    for fragment in expected_fragments:
        assert fragment in result.command

def test_qr_walkthrough(qr_service):
    """
    Test the generation of QR codes for the entire walkthrough.
    """

    STEP1_COMMAND = qr_service.create_step1()
    STEP2_COMMAND = qr_service.create_step2()
    STEP3_COMMAND = qr_service.multi_step()
    STEP4_COMMAND = qr_service.create_step8() # needs to run again after multi_step
    STEP5_COMMAND = qr_service.create_macs("00:11:22:33:44:55", "66:77:88:99:AA:BB")
    STEP6_COMMAND = qr_service.create_step11()

    logger.info("TEST: Step 1")
    logger.info("=" * 70)
    assert_generated_qr(STEP1_COMMAND, "step1", ["root"])
    logger.info("=" * 70)

    logger.info("TEST: Step 2")
    logger.info("=" * 70)
    assert_generated_qr(STEP2_COMMAND, "step2", ["default"])
    logger.info("=" * 70)

    logger.info("TEST: Functional Test")
    logger.info("=" * 70)
    assert_generated_qr(STEP3_COMMAND, "functional_test", [
        "ls /dev/sd[a-e]",
        "timeout 2s loopback /dev/port0[2-4] -q",
        "timeout 2s loopback /dev/port0[5-8] -q",
        "ifconfig eth1 up",
        "sleep 5",
        "ethtool eth1",
        "echo 1 | tee /sys/class/leds/acm7000:green:sig_*/brightness",
        "emd -i sysfs -c 4"
    ],)
    logger.info("=" * 70)

    logger.info("TEST: Step 4 (config step 8)")
    logger.info("=" * 70)
    assert_generated_qr(STEP4_COMMAND, "step8", ["emd -i sysfs -c 4"])
    logger.info("=" * 70)

    logger.info("TEST: Step 5 (MAC programming)")
    logger.info("=" * 70)
    assert_generated_qr(STEP5_COMMAND, "mac_programming", [
        "ethaddr=00:11:22:33:44:55",
        "eth1addr=66:77:88:99:AA:BB"
    ])
    logger.info("=" * 70)

    logger.info("TEST: Step 6 (config step 11)")
    logger.info("=" * 70)
    assert_generated_qr(STEP6_COMMAND, "step11", ["step11"])
    logger.info("=" * 70)
    