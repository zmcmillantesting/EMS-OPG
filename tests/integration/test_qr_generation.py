"""
Integration Tests - QR Generation

These tests verify that:

1. QR commands are generated correctly.
2. MAC placeholders are replaced.
3. PNG images are written to cache/qr.
4. Images can be scanned manually.
5. A detailed log is written to logs/qr_generation_test.log.
"""

import logging

import pytest

from ems_opg.core.paths_manager import PathManager
from ems_opg.services.qr_service import QRService


# ---------------------------------------------------------------------
# Setup logging
# ---------------------------------------------------------------------

paths = PathManager()
paths.create_directories()

LOG_FILE = paths.logs_dir / "qr_generation_test.log"

logger = logging.getLogger("qr_generation_test")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers when pytest reloads modules
if not logger.handlers:

    file_handler = logging.FileHandler(LOG_FILE, mode="w")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


# ---------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def qr_service():
    """
    Creates one QRService for the entire test module.
    QR images are written into cache/qr.
    """

    return QRService(
        output_directory=paths.qr_cache
    )


# ---------------------------------------------------------------------
# Test 1
# ---------------------------------------------------------------------

def test_multi_step_generation(qr_service):

    logger.info("=" * 70)
    logger.info("TEST: Functional Workflow")
    logger.info("=" * 70)

    command = qr_service.multi_step()

    result = qr_service.generator.generate(
        command,
        "functional_test",
    )

    logger.info("Output File : %s", result.path)
    logger.info("Command:")
    logger.info(result.command)

    assert result.path.exists()
    assert result.path.suffix == ".png"

    assert "ls /dev/sd[a-e]" in result.command
    assert "loopback" in result.command
    assert "ethtool" in result.command

    logger.info("PASS\n")


# ---------------------------------------------------------------------
# Test 2
# ---------------------------------------------------------------------

def test_mac_generation(qr_service):

    logger.info("=" * 70)
    logger.info("TEST: MAC Programming")
    logger.info("=" * 70)

    mac1 = "00:11:22:33:44:55"
    mac2 = "00:11:22:33:44:56"

    command = qr_service.create_macs(
        mac1,
        mac2,
    )

    result = qr_service.generator.generate(
        command,
        "mac_programming",
    )

    logger.info("Output File : %s", result.path)
    logger.info("MAC1        : %s", mac1)
    logger.info("MAC2        : %s", mac2)
    logger.info("Command:")
    logger.info(result.command)

    assert result.path.exists()

    assert f"ethaddr={mac1}" in result.command
    assert f"eth1addr={mac2}" in result.command

    assert "{mac1}" not in result.command
    assert "{mac2}" not in result.command

    logger.info("PASS\n")


# ---------------------------------------------------------------------
# Test 3
# ---------------------------------------------------------------------

def test_complete_workflow(qr_service):

    logger.info("=" * 70)
    logger.info("TEST: Complete Workflow")
    logger.info("=" * 70)

    mac1 = "00:11:22:33:44:55"
    mac2 = "00:11:22:33:44:56"

    functional = qr_service.multi_step()

    mac_programming = qr_service.create_macs(
        mac1,
        mac2,
    )

    complete_command = (
        f"{functional} && sleep 2 && {mac_programming}"
    )

    result = qr_service.generator.generate(
        complete_command,
        "complete_test",
    )

    logger.info("Output File : %s", result.path)
    logger.info("Command:")
    logger.info(result.command)

    assert result.path.exists()

    assert "ls /dev/sd[a-e]" in result.command
    assert "loopback" in result.command
    assert "ethtool" in result.command

    assert f"ethaddr={mac1}" in result.command
    assert f"eth1addr={mac2}" in result.command

    assert "{mac1}" not in result.command
    assert "{mac2}" not in result.command

    logger.info("PASS\n")


# ---------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------

def test_qr_summary():

    logger.info("=" * 70)
    logger.info("QR GENERATION TESTS COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)

    logger.info("Generated Images:")

    for image in sorted(paths.qr_cache.glob("*.png")):
        logger.info(" - %s", image.name)

    logger.info("")

    assert True