from ems_opg.QR_Codes.qr_generator import QRGenerator
from ems_opg.QR_Codes import qr_templates
from ems_opg.config.config_manager import ConfigurationManager
from ems_opg.core.paths_manager import PathManager


class QRService:

    def __init__(self, output_directory):
        paths = PathManager()
        self.generator = QRGenerator(output_directory)
        self.config = ConfigurationManager(paths.config_file)

    def create_step3(self):

        return self.generator.generate(
            qr_templates.STEP3,
            "step3",
        )

    def create_step8(self, mac1):

        command = qr_templates.STEP8.format(
            mac1=mac1,
        )

        return self.generator.generate(
            command,
            "step8",
        )

    def create_step9(self, mac2):

        command = qr_templates.STEP9.format(
            mac2=mac2,
        )

        return self.generator.generate(
            command,
            "step9",
        )

# combine steps 
    def multi_step(self):

        steps = self.config.get_workflow("functional_test")
        command = "; ".join(
            self.config.get_qr_command(step)
            for step in steps
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

        return command