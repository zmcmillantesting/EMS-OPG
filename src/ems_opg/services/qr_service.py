class QRService:

    def generate_step8(self, device):

        command = (
            f"setfset -u ethaddr="
            f"{device.mac_address}"
        )

        return self.generate(command)

    def generate_step9(self, device):

        command = (
            f"setfset -u eth1addr="
            f"{device.mac_address}"
        )

        return self.generate(command)