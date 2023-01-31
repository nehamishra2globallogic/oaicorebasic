import os
import subprocess

import docker

BACKGROUND_LOG_DIR = "/tmp/oai-docker-api/"


def _run_cmd_in_shell(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True)
    return res.stdout.decode()


class DockerApi:
    running_background_tasks = {}

    def __init__(self):
        self.client = docker.APIClient(base_url='unix://var/run/docker.sock')

    def check_health_status(self, container_list):
        containers = self.client.containers(all=True)
        count = 0
        for container in containers:
            healthy_list = []
            name = container["Names"][0][1:]
            if name not in container_list:
                continue

            inspect = self.client.inspect_container(name)
            state = inspect["State"]
            if state.get("Health"):
                health_status = state["Health"]["Status"]
                if health_status != "healthy":
                    raise Exception(f"At least one container is not healthy: {name}: {health_status}")
                count += 1
                healthy_list.append(name)

        if count != len(container_list):
            raise Exception(f"There are {count}/{len(container_list)} healthy containers")

    def store_all_logs(self, log_dir, container_list=None):
        containers = self.client.containers(all=True)
        for container in containers:
            name = container["Names"][0][1:]
            if container_list and name not in container_list:
                continue

            log = self.client.logs(container).decode()
            file_name = os.path.join(log_dir, name)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            with open(file_name, "w") as f:
                f.write(log)

    def get_log(self, container):
        return self.client.logs(container).decode()

    def exec_on_container(self, container, cmd):
        proc = self.client.exec_create(container, cmd)
        result = self.client.exec_start(proc["Id"]).decode()
        status = self.client.exec_inspect(proc["Id"])
        if status["ExitCode"] != 0:
            raise Exception(f"Executing command {cmd} failed: {result}")
        return result

    def exec_on_container_background(self, container, cmd):
        proc = self.client.exec_create(container, cmd)
        stream = self.client.exec_start(proc["Id"], detach=False, stream=True)
        self.running_background_tasks[proc["Id"]] = (container, stream)
        return proc["Id"]

    def _prepare_log_dir(self, container):
        try:
            self.exec_on_container(container, f"mkdir {BACKGROUND_LOG_DIR}")
        except:
            pass  # ignore if already exists

    def stop_background_process(self, proc_id):
        container, _ = self.running_background_tasks[proc_id]
        status = self.client.exec_inspect(proc_id)
        # this gives me the system-wide PID, but we need the namespace PID
        pid = status["Pid"]
        docker_pid = _run_cmd_in_shell([f"grep NSpid /proc/{pid}/status | cut -f3"])
        if not docker_pid:
            raise Exception("Could not stop background task. Is it running?")
        try:
            self.exec_on_container(container, f"kill -9 {docker_pid}")
        except Exception as e:
            print(f"Could not stop background task: {e}")

    def stop_all_background_processes(self, container):
        for proc_id in self.running_background_tasks:
            on_container, _ = self.running_background_tasks[proc_id]
            if container == on_container:
                self.stop_background_process(proc_id)

    def is_process_finished(self, proc_id):
        status = self.client.exec_inspect(proc_id)
        if status["Running"]:
            raise Exception("Process is still running")
        return False

    def get_process_result(self, proc_id):
        self.is_process_finished(proc_id)
        status = self.client.exec_inspect(proc_id)

        container, stream = self.running_background_tasks[proc_id]
        res = ""
        for line in stream:
            res += line.decode()

        if status["ExitCode"] != 0:
            raise Exception(f"Background Task failed: Return code != 0: {res}")
        return res
