"""
QR Command Validator

Validates QR command payloads before they are encoded into
a QR code.

This validator DOES NOT inspect PNG files.
It validates the command string itself.
"""

from dataclasses import dataclass
import re


@dataclass
class ValidationResult:
    """
    Result returned by QRValidator.
    """

    valid: bool
    errors: list[str]


class QRValidator:
    """
    Validates QR commands before QR generation.
    """

    def __init__(self):

        self.required_functional_steps = [

            "ls /dev/sd",

            "loopback /dev/port0[2-4]",

            "loopback /dev/port0[5-8]",

            "ifconfig",

            "ethtool",

            "root",

            "default",

        ]

    # --------------------------------------------------

    def validate(self, command: str) -> ValidationResult:

        errors = []

        #
        # Empty command
        #

        if command is None:

            errors.append("Command is None.")

            return ValidationResult(False, errors)

        if not command.strip():

            errors.append("Command is empty.")

        #
        # Placeholder replacement
        #

        placeholders = re.findall(r"{.*?}", command)

        if placeholders:

            errors.append(
                f"Unresolved placeholders: {', '.join(placeholders)}"
            )

        #
        # Double &&
        #

        if "&& &&" in command:

            errors.append(
                "Malformed command contains consecutive &&."
            )

        #
        # Triple &&
        #

        if "&&&" in command:

            errors.append(
                "Malformed command contains &&&."
            )

        #
        # Unresolved MAC address placeholders 
        #

        if "{mac1}" in command or "{mac2}" in command:
            errors.append(
                "Unresolved MAC address placeholders: {mac1} or {mac2}")

        return ValidationResult(

            valid=len(errors) == 0,

            errors=errors,

        )

    # --------------------------------------------------

    def validate_functional_workflow(
        self,
        command: str,
    ) -> ValidationResult:

        result = self.validate(command)

        errors = result.errors.copy()

        for step in self.required_functional_steps:

            if step not in command:

                errors.append(
                    f"Missing workflow step: {step}"
                )

        return ValidationResult(

            valid=len(errors) == 0,

            errors=errors,

        )

    def validate_mac_programming(
            self,
            command: str,
    ) -> ValidationResult:
        result = self.validate(command)

        errors = result.errors.copy()

        # Check for ethaddr and eth1addr

        if "ethaddr=" not in command:

            errors.append(
                "Missing MAC address assignment: ethaddr"
            )

        if "eth1addr=" not in command:

            errors.append(
                "Missing MAC address assignment: eth1addr"
            )

        if "{mac1}" in command or "{mac2}" in command:
            errors.append(
                "Unresolved MAC address placeholders: {mac1} or {mac2}")

        return ValidationResult(

            valid=len(errors) == 0,

            errors=errors,

        )

    def validate_step10(self, command:str) -> ValidationResult:
        result = self.validate(command)

        errors = result.errors.copy()

        if "setfset | grep eth0 && setfset | grep eth1" not in command:
            errors.append("Invalid step10 command.")

        return ValidationResult(

            valid=len(errors) == 0,

            errors=errors,

        )
