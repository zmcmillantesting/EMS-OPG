import pytest

from ems_opg.QR_Codes.qr_validator import QRValidator


@pytest.fixture
def validator():

    return QRValidator()


# -----------------------------------------------------------


def test_valid_command(validator):

    command = (
        "ls /dev/sd[a-e] && "
        "timeout 2s loopback /dev/port0[2-4] -q"
        "setfset | grep eth0 && setfset | grep eth1"
    )

    result = validator.validate(command)

    assert result.valid
    assert result.errors == []


# -----------------------------------------------------------


def test_empty_command(validator):

    result = validator.validate("")

    assert not result.valid

    assert "Command is empty." in result.errors


# -----------------------------------------------------------


def test_none_command(validator):

    result = validator.validate(None)

    assert not result.valid

    assert "Command is None." in result.errors


# -----------------------------------------------------------


def test_mac_placeholder_detected(validator):

    command = "setfset -u ethaddr={mac1}"

    result = validator.validate(command)

    assert not result.valid

    assert "Unresolved placeholders" in result.errors[0]


# -----------------------------------------------------------


def test_multiple_placeholders(validator):

    command = (
        "setfset -u ethaddr={mac1} && "
        "setfset -u eth1addr={mac2}"
    )

    result = validator.validate(command)

    assert not result.valid

    assert "{mac1}" in result.errors[0]

    assert "{mac2}" in result.errors[0]


# -----------------------------------------------------------


def test_double_and_detected(validator):

    command = "ls && && pwd"

    result = validator.validate(command)

    assert not result.valid

    assert any(
        "consecutive &&" in error
        for error in result.errors
    )


# -----------------------------------------------------------


def test_functional_workflow_passes(validator):

    command = (
        "ls /dev/sd[a-e] && "
        "timeout 2s loopback /dev/port0[2-4] -q && "
        "timeout 2s loopback /dev/port0[5-8] -q && "
        "ifconfig eth1 up && sleep 5 && ethtool eth1"
    )

    result = validator.validate_functional_workflow(command)

    assert result.valid


# -----------------------------------------------------------


def test_missing_ethtool(validator):

    command = (
        "ls /dev/sd[a-e] && "
        "timeout 2s loopback /dev/port0[2-4] -q"
    )

    result = validator.validate_functional_workflow(command)

    assert not result.valid

    assert any(
        "ethtool" in error
        for error in result.errors
    )

def test_step_10(validator):
    command = "setfset | grep eth0 && setfset | grep eth1"
    result = validator.validate_step10(command)
    assert result.valid