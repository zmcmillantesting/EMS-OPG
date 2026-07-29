from pathlib import Path
from ems_opg.QR_Codes.qr_result import QRResult

import segno

class QRGenerator:

    def __init__(self, output_directory):

        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate(
        self,
        command,
        filename,
    ):

        qr = segno.make(
            command,
            error="M",
        )

        output_file = (
            self.output_directory
            / f"{filename}.png"
        )

        qr.save(
            output_file,
            scale=8,
        )

        return QRResult(
            filename=output_file.name,
            path=output_file,
            command=command
        )