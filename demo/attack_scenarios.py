"""Replay synthetic observations through the same API as imported flows."""
from .traffic_generator import TrafficGenerator


class DemoScenario:
    def __init__(self, target_host="127.0.0.1", api_url=None):
        self.generator = TrafficGenerator(target_host, api_url)

    def run_phase_1_normal(self):
        return self.generator.submit("normal")

    def run_phase_2_recon(self):
        return self.generator.submit("recon")

    def run_phase_3_credential_access(self):
        return self.generator.submit("credential")

    def run_phase_4_lateral_movement(self):
        return self.generator.submit("lateral")

    def run_phase_5_c2(self):
        return self.generator.submit("c2")

    def run_phase_6_exfiltration(self):
        return self.generator.submit("exfiltration")
