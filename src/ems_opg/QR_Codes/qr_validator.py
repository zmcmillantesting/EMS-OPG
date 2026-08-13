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

            "loopback",

            "ifconfig",

            "ethtool",

            "echo 1 | tee /sys/class/leds/acm7000:green:sig_*/brightness",

            "emd -i sysfs -c 4",

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

        if not isinstance(command, str):

            errors.append("Command must be a string.")

            return ValidationResult(False, errors)

        if not command:

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

        # Check for ethaddr= and ethaddr1=

        if "ethaddr=" not in command or "ethaddr1=" not in command:

            errors.append(
                "Missing MAC address assignment: eth0 and/or eth1"
            )


        if "{mac1}" in command or "{mac2}" in command:
            errors.append(
                "Unresolved MAC address placeholders: {mac1} or {mac2}")

        return ValidationResult(

            valid=len(errors) == 0,

            errors=errors,

        )

    def validate_step8(self, command:str) -> ValidationResult:
        result = self.validate(command)

        errors = result.errors.copy()

        if "emd -i sysfs -c 4" not in command:
            errors.append("Invalid step8 command.")

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

    def validate_user(self, command:str) -> ValidationResult:
        result = self.validate(command)

        errors = result.errors.copy()

        if "root" not in command:
            errors.append("Invalid user command.")

        return ValidationResult(

            valid=len(errors) == 0,

            errors=errors,

        )

    def validate_password(self, command:str) -> ValidationResult:
        result = self.validate(command)

        errors = result.errors.copy()

        if "default" not in command:
            errors.append("Invalid password command.")

        return ValidationResult(

            valid=len(errors) == 0,

            errors=errors,

        )