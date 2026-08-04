from ems_opg.QR_Codes.qr_generator import QRGenerator
# from ems_opg.QR_Codes import qr_templates
from ems_opg.QR_Codes.qr_validator import QRValidator
from ems_opg.config.config_manager import ConfigurationManager
from ems_opg.core.paths_manager import PathManager
from ems_opg.core.exceptions import QRValidationError


class QRService:

    def __init__(self, output_directory):
        paths = PathManager()
        self.generator = QRGenerator(output_directory)
        self.config = ConfigurationManager(paths.config_file)
        self.validator = QRValidator()

    def create_step1(self):
        command = self.config.get_qr_command("step1")

        validation = self.validator.validate_user(command)
        if not validation.valid:
            raise QRValidationError(
                "\n".join(validation.errors)
            )

        return self.generator.generate(
            command,
            "step1",
        )

    def create_step2(self):
        command = self.config.get_qr_command("step2")

        validation = self.validator.validate_password(command)
        if not validation.valid:
            raise QRValidationError(
                "\n".join(validation.errors)
            )
        return self.generator.generate(
            command,
            "step2",
        )


    def create_step8(self):

        command = self.config.get_qr_command("step8")
        validation = self.validator.validate_step8(command)
        if not validation.valid:
            raise QRValidationError(
                "\n".join(validation.errors)
            )

        return self.generator.generate(
            command,
            "step8",
        )

    # def create_step9(self, mac2):

    #     command = qr_templates.STEP9.format(
    #         mac2=mac2,
    #     )

    #     validation = self.validator.validate_step9(command)
    #     if not validation.valid:
    #         raise QRValidationError(
    #             "\n".join(validation.errors)
    #         )

    #     return self.generator.generate(
    #         command,
    #         "step9",
    #     )

# combine steps 3,5,4,6
    def multi_step(self):

        steps = self.config.get_workflow("functional_test")
        command = "; ".join(
            self.config.get_qr_command(step)
            for step in steps
        )

        validation = self.validator.validate_functional_workflow(command)
        if not validation.valid:
            raise QRValidationError(
                "\n".join(validation.errors)
            )

        return command


# combine both mac address comands into 1 step
    def create_macs(self, ethaddr, ethaddr1):

        templates = self.config.get_workflow("combined_macs")
        command = " && ".join( 
            self.config.format_qr_command(
            step,
            mac1=ethaddr,
            mac2=ethaddr1,
            )
        for step in templates
        )

        validation = self.validator.validate_mac_programming(command)
        if not validation.valid:
            raise QRValidationError(
                "\n".join(validation.errors)
            )   

        return command

    def create_step11(self):
        command = self.config.get_qr_command("step11")

        validation = self.validator.validate_step11(command)
        if not validation.valid:
            raise QRValidationError(
                "\n".join(validation.errors)
            )
        return command

        