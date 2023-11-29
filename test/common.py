import os
import subprocess
import logging
import sys
import yaml

GENERATED_DIR = "out"

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format="[%(asctime)s] %(levelname)8s: %(message)s"
)

DIR_PATH = os.path.split(os.path.abspath(__file__))[0]
OUT_PATH = os.path.join(DIR_PATH, GENERATED_DIR)
LOG_DIR = os.path.join(OUT_PATH, "logs")


# import common ci scripts
# sys.path.append(os.path.join(DIR_PATH, "../ci-scripts/common/python"))
# from cls_cmd import LocalCmd
#
# cmd = LocalCmd()


def prepare_folders():
    os.makedirs(OUT_PATH, exist_ok=True)


def __docker_subprocess(args):
    try:
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, timeout=60)
        logging.info(res.stdout.decode("utf-8").strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logging.error(e.stdout.decode("utf-8").strip())
        raise e


def start_docker_compose(path, container=None):
    logging.info(f"Docker-compose file: {path}")
    if container:
        __docker_subprocess(["docker-compose", "-f", path, "up", "-d", container])
    else:
        __docker_subprocess(["docker-compose", "-f", path, "up", "-d"])


def stop_docker_compose(path):
    __docker_subprocess(["docker-compose", "-f", path, "stop", "-t", "5"])


def down_docker_compose(path):
    __docker_subprocess(["docker-compose", "-f", path, "down", "-t", "5"])


def get_docker_compose_services(docker_compose_file):
    all_services = []
    with open(docker_compose_file) as f:
        parsed = yaml.safe_load(f)
        for service in parsed["services"]:
            all_services.append(service)

    return all_services
