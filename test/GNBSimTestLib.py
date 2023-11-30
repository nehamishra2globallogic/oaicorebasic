import ipaddress

from common import *
from docker_api import DockerApi

GNBSIM_TEMPLATE = "template/docker-compose-gnbsim.yaml"
GNBSIM_FIRST_IP = "192.168.79.160"
GNBSIM_FIRST_MSIN = 31


class GNBSimTestLib:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self):
        self.docker_api = DockerApi()
        self.gnbsims = []
        prepare_folders()

    def __generate_msin(self):
        return str(GNBSIM_FIRST_MSIN + len(self.gnbsims)).zfill(10)

    def __generate_ip(self):
        ip = ipaddress.ip_address(GNBSIM_FIRST_IP) + len(self.gnbsims)
        return str(ip)

    def __generate_name(self):
        return f"gnbsim-{len(self.gnbsims) + 1}"

    def __get_docker_compose_path(self, gnbsim_name):
        if gnbsim_name not in self.gnbsims:
            raise Exception(f"gnbsim {gnbsim_name} is not in config. You have to call prepare_gnbsim first")
        return os.path.join(get_out_dir(), f"docker-compose-{gnbsim_name}.yaml")

    def prepare_gnbsim(self):
        """
        Prepares a gnbsim by copying the template
        :return: container name of this gnbsim
        """

        with open(os.path.join(DIR_PATH, GNBSIM_TEMPLATE)) as f:
            parsed = yaml.safe_load(f)
            name = ""
            for service in parsed["services"].copy():
                gnb = parsed["services"].pop(service)
                for i, elem in enumerate(gnb["environment"]):
                    elem = elem.replace("REPLACE_MSIN", self.__generate_msin())
                    elem = elem.replace("REPLACE_IP", self.__generate_ip())
                    gnb["environment"][i] = elem
                gnb["networks"]["public_test_net"]["ipv4_address"] = self.__generate_ip()
                # now replace with new name
                name = self.__generate_name()
                gnb["container_name"] = name
                parsed["services"][name] = gnb
                self.gnbsims.append(name)
                break
            if name == "":
                raise Exception("Reading docker-compose for gnbsim failed")
            with (open(self.__get_docker_compose_path(name), "w")) as out_file:
                yaml.dump(parsed, out_file)
            return name

    def check_gnbsim_health_status(self, gnbsim_container):
        self.docker_api.check_health_status([gnbsim_container])

    def collect_all_gnbsim_logs(self):
        self.docker_api.store_all_logs(get_log_dir(), self.gnbsims)

    def check_gnbsim_ongoing(self, container):
        log = self.docker_api.get_log(container)
        for line in log.split("\n"):
            if "UE address" in line:
                line_split = line.split(":")
                if "nil" in line_split[-1]:
                    logging.info("PDU session establishment failed")
                    return ""
                else:
                    logging.info("PDU session establishment successful")
                    return line_split[-1].strip()
        raise Exception("PDU session establishment ongoing")

    def get_gnbsim_ip(self, container):
        ip = self.check_gnbsim_ongoing(container)
        if ip == "":
            raise Exception("PDU session establishment failed")
        return ip

    def start_gnbsim(self, gnbsim_name):
        start_docker_compose(self.__get_docker_compose_path(gnbsim_name))

    def stop_gnbsim(self, gnbsim_name):
        stop_docker_compose(self.__get_docker_compose_path(gnbsim_name))

    def down_gnbsim(self, gnbsim_name):
        down_docker_compose(self.__get_docker_compose_path(gnbsim_name))

    def create_gnbsim_docu(self):
        if len(self.gnbsims) == 0:
            return ""
        docu = " = GNBSIM Tester Image = \n"
        docu += create_image_info_header()
        size, date = self.docker_api.get_image_info(image_tags["gnbsim"])
        docu += create_image_info_line("gnbsim", image_tags["gnbsim"], date, size)
        return docu

    def ping_from_gnbsim(self, gnbsim_name, target_ip, count=4):
        self.docker_api.exec_on_container(gnbsim_name, f"ping -I {self.get_gnbsim_ip(gnbsim_name)} -c {count} {target_ip}")
