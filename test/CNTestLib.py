import time

import yaml

from docker_api import DockerApi


def get_docker_compose_services(docker_compose_file):
    all_services = []
    with open(docker_compose_file) as f:
        parsed = yaml.safe_load(f)
        for service in parsed["services"]:
            all_services.append(service)

    return all_services


class CNTestLib:
    running_iperf_servers = {}
    running_iperf_clients = {}
    last_iperf_result = {}

    def __init__(self):
        self.docker_api = DockerApi()

    def check_cn_health_status(self, docker_compose_file):
        all_services = get_docker_compose_services(docker_compose_file)
        self.docker_api.check_health_status(all_services)

    def collect_all_logs(self, log_dir, docker_compose_file):
        all_services = get_docker_compose_services(docker_compose_file)
        self.docker_api.store_all_logs(log_dir, all_services)

    def get_gnbsim_ip(self, container):
        log = self.docker_api.get_log(container)
        for line in log.split("\n"):
            if "UE address" in line:
                line_split = line.split(":")
                if "nil" in line_split[-1]:
                    raise Exception("UE IP address is null. PDU session establishment not successful")
                else:
                    return line_split[-1].strip()
        raise Exception("PDU session establishment ongoing")

    def configure_default_qos(self, five_qi=9, session_ambr=50):
        print("TODO implement me")

    def add_qos_flow_on_pcf(self, five_qi, match, gfbr=10, mfbr=11):
        print("TODO implement me")
        # the plan is to write the yaml files here and if necessary restart PCF

    def start_iperf3_server(self, container, port=39265, bind_ip=""):
        cmd = f"iperf3 -s -i 2 -p {port}"
        if bind_ip:
            cmd += f" -B {bind_ip}"

        proc_id = self.docker_api.exec_on_container_background(container, cmd)
        self.running_iperf_servers[f"{container}-{port}"] = proc_id
        # wait until server is ready
        time.sleep(1)

    def stop_iperf3_server(self, container, port=39265):
        proc_id = self.running_iperf_servers[f"{container}-{port}"]
        self.docker_api.stop_background_process(proc_id)

    def start_iperf3_client(self, container, bind_ip, server, port=39265, bandwidth="", duration=20):
        cmd = f"iperf3 -t {duration} -i 2 -c {server} -p {port}"
        if bind_ip:
            cmd += f" -B {bind_ip}"
        if bandwidth:
            b = int(bandwidth) * 1024 * 1024
            cmd += f" -b {b}"
        print(f"Starting iperf3 Test: {cmd}")
        proc_id = self.docker_api.exec_on_container_background(container, cmd)
        self.running_iperf_clients[container] = proc_id

    def iperf3_is_finished(self, container):
        proc_id = self.running_iperf_clients[container]
        self.docker_api.is_process_finished(proc_id)
        self.last_iperf_result[container] = self.docker_api.get_process_result(proc_id)

    def iperf3_results_should_be(self, container, bandwidth, interval=0.1):
        res = self.last_iperf_result[container]
        bandwidth = float(bandwidth)
        interval = float(interval)

        last_line = res.split("\n")[-4]
        bandwidth_receiver = float(last_line.split()[6])
        unit = last_line.split()[7]

        if "Gbit" in unit:
            bandwidth_receiver = bandwidth_receiver * 1024

        min_b = bandwidth - (bandwidth * interval)
        max_b = bandwidth + (bandwidth * interval)

        print(res)

        if bandwidth_receiver < min_b or bandwidth_receiver > max_b:
            raise Exception(f"Bandwidth should be in interval [{min_b}, {max_b}], but it is {bandwidth_receiver}")
