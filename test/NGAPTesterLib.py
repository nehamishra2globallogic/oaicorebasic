import re
import shutil

from docker_api import DockerApi
from common import *

NGAP_TESTER_TEMPLATE_DOCKER_COMPOSE = "template/docker-compose-ngap-tester.yaml"
NGAP_TESTER_TEMPLATE_CONFIG = "template/ngap_tester_template_config.yaml"


class NGAPTesterLib:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self):
        self.docker_api = DockerApi()
        self.docker_compose_path = ""
        self.conf_path = ""
        self.name = ""
        self.tc_name = ""

    def prepare_ngap_tester(self, tc_name, mt_profile="default"):
        self.tc_name = tc_name
        self.name = f"ngap-tester-{tc_name}-{mt_profile}"
        self.docker_compose_path = os.path.join(OUT_PATH, f"docker-compose-ngap-tester-{tc_name}-{mt_profile}.yaml")
        self.conf_path = os.path.join(OUT_PATH, "ngap_tester_config.yaml")  # we only have one config for all the tests
        shutil.copy(os.path.join(DIR_PATH, NGAP_TESTER_TEMPLATE_CONFIG), self.conf_path)

        with open(os.path.join(DIR_PATH, NGAP_TESTER_TEMPLATE_DOCKER_COMPOSE)) as f:
            parsed = yaml.safe_load(f)
            for service in parsed["services"].copy():
                if service != "REPLACE_SERVICE":
                    continue
                ngap = parsed["services"].pop(service)
                ngap["command"] = ngap["command"].replace("REPLACE_TEST", tc_name)
                ngap["command"] = ngap["command"].replace("REPLACE_MT_PROFILE", mt_profile)
                ngap["container_name"] = self.name
                parsed["services"][self.name] = ngap

            with (open(self.docker_compose_path, "w")) as out_file:
                yaml.dump(parsed, out_file)
            return self.name

    def check_ngap_tester_done(self):
        self.docker_api.check_container_stopped(self.name)

    def __read_ngap_tester_results(self):
        log = self.docker_api.get_log(self.name)
        test_ended = False
        test_passed = False
        description = ""
        for line in log.splitlines():
            result = re.search('Scenario *: Status *: Description', line)
            if result is not None:
                test_ended = True
            result = re.search(f'{self.tc_name} *: (?P<status>[A-Z]+) *: (?P<description>.*$)', line)
            if result is not None and test_ended:
                if result.group('status') == 'PASSED':
                    test_passed = True
                description = result.group('description')
                description = re.sub('NOT YET VALIDATED - ', '', description)
        return test_ended, test_passed, description

    def get_ngap_tester_description(self):
        self.check_ngap_tester_done()
        res = self.__read_ngap_tester_results()
        if res[0]:
            return res[2]
        else:
            return "There was an issue in starting the test. Please see the logs"

    def check_ngap_tester_result(self):
        self.check_ngap_tester_done()
        res = self.__read_ngap_tester_results()
        if not res[1]:
            raise Exception("NGAP Tester Test did not pass")

    def start_ngap_tester(self):
        # starts trafficgen and ngap tester
        start_docker_compose(self.docker_compose_path)

    def stop_ngap_tester(self):
        stop_docker_compose(self.docker_compose_path)

    def down_ngap_tester(self):
        down_docker_compose(self.docker_compose_path)

    def collect_all_ngap_tester_logs(self):
        all_services = get_docker_compose_services(self.docker_compose_path)
        self.docker_api.store_all_logs(LOG_DIR, all_services)
