"""
Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
contributor license agreements.  See the NOTICE file distributed with
this work for additional information regarding copyright ownership.
The OpenAirInterface Software Alliance licenses this file to You under
the OAI Public License, Version 1.1  (the "License"); you may not use this file
except in compliance with the License.
You may obtain a copy of the License at

      http://www.openairinterface.org/?page_id=698

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
------------------------------------------------------------------------------
For more information about the OpenAirInterface (OAI) Software Alliance:
      contact@openairinterface.org

------------------------------------------------------------------------------
"""
import argparse
import logging
import os
import re
import sys
import subprocess
from subprocess import PIPE, STDOUT

DOCKER_COMPOSE_FOLDER_NAME = "docker-compose"
DOCUMENT_FOLDER_NAME = "docs"

RED_COLOR = "\x1b[31;20m"
GREEN_COLOR = "\x1b[32;20m"
RESET_COLOR = "\x1b[0m"

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format="%(message)s"
)

try:
    from robot.api import logger
    from robot.libraries.BuiltIn import BuiltIn

    USE_ROBOT = True
except:
    USE_ROBOT = False


class CheckTutorial:
    docker_compose_dir = ""

    def __init__(self):
        self.cmds_per_block = {}
        self.tutorial_text = ""
        self.tutorial_name = ""
        self.h2_pattern = re.compile(r"^## (.*)", re.MULTILINE)
        self.shell_pattern = re.compile(r"`{3} shell\n([\S\s]+?)`{3}")
        self.cmd_pattern = re.compile(r"\$: (.*)")
        self.bi = BuiltIn()
        self.command_status = {}
        global USE_ROBOT

        # When not running in robot context, this will fail
        try:
            self.bi.run_keyword("Log", "Executing in robot")
        except:
            USE_ROBOT = False

        self.all_passed = True

    def log_msg(self, msg, extra_kw=False, lvl=logging.INFO):
        color_msg = msg
        log_string = "INFO"
        if lvl == logging.ERROR:
            color_msg = RED_COLOR + msg + RESET_COLOR
            log_string = "ERROR"
        elif lvl == logging.INFO:
            color_msg = GREEN_COLOR + msg + RESET_COLOR

        if USE_ROBOT:
            self.bi.log_to_console(msg)
            if extra_kw:
                self.bi.run_keyword("Log", msg, log_string)
                return  # dont log twice
        logging.log(lvl, color_msg)

    def prepare_tutorial(self, filename):
        base_path = os.path.split(os.path.abspath(filename))
        self.tutorial_name = base_path[1]
        base_path = os.path.split(base_path[0])
        self.docker_compose_dir = os.path.join(base_path[0], DOCKER_COMPOSE_FOLDER_NAME)

        if not os.path.exists(self.docker_compose_dir):
            raise Exception(f"Directory {self.docker_compose_dir} does not exist")

        with open(filename, "r") as f:
            self.tutorial_text = f.read()

        self.extract_cmds_per_h2_block()

    def extract_cmds_per_h2_block(self):
        last_end = -1
        last_header = ""
        for m in self.h2_pattern.finditer(self.tutorial_text):
            end = m.end(1)

            if last_end >= 0:
                self.extract_shell_commands(last_header, last_end, end)
            last_end = end
            last_header = m.group(1)

        # last section
        if last_end >= 0:
            self.extract_shell_commands(last_header, last_end, len(self.tutorial_text))

    def extract_shell_commands(self, title, start, end):
        cmds = []
        text_between_h2s = self.tutorial_text[start:end]
        shell_blocks = self.shell_pattern.findall(text_between_h2s)
        for block in shell_blocks:
            for cmd in self.cmd_pattern.findall(block):
                cmds.append(cmd)
        if len(cmds) > 0:
            self.cmds_per_block[title] = cmds

    def execute_all_tutorial_commands(self):
        for key in self.cmds_per_block:
            self.log_msg(f"Executing commands of Section {key}", True)
            for cmd in self.cmds_per_block[key]:
                self.log_msg(f"Executing command {cmd}", True)
                self.subprocess_call(cmd)

        if not self.all_passed:
            if USE_ROBOT:
                self.bi.fail("Tutorial failed")

    def subprocess_call(self, command):
        popen = subprocess.Popen(command, shell=True, universal_newlines=True, cwd=self.docker_compose_dir, stdout=PIPE,
                                 stderr=STDOUT)
        for stdoutLine in popen.stdout:
            self.log_msg(stdoutLine, lvl=logging.DEBUG)
        popen.stdout.close()
        return_code = popen.wait()
        if return_code == 0:
            self.command_status[command] = True
        else:
            self.command_status[command] = False
            self.all_passed = False
            self.log_msg(f"Command {command} failed!", True, logging.ERROR)

    def print_tutorial_summary(self):
        if self.all_passed:
            final_result = "PASS"
            level = logging.INFO
        else:
            final_result = "FAIL"
            level = logging.ERROR

        self.log_msg(f"\nFinal result for the tutorial {self.tutorial_name} is {final_result}", lvl=level)

        pass_count = 0
        fail_count = 0
        for command in self.command_status:
            if self.command_status[command]:
                pass_count += 1
                self.log_msg(f"PASS : {command}", lvl=logging.INFO)
            else:
                fail_count += 1
                self.log_msg(f"FAIL : {command}", lvl=logging.ERROR)

        self.log_msg(f"{pass_count} out of {pass_count + fail_count} commands passed")
        if self.all_passed:
            return 0
        return -1


def _parse_args() -> argparse.Namespace:
    """Parse the command line args

    Returns:
        argparse.Namespace: the created parser
    """
    example_text = '''example:
        python3 checkTutorial.py --tutorial DEPLOY_SA5G_BASIC_STATIC_UE_IP.md'''

    parser = argparse.ArgumentParser(description='Run the tutorials to see they are executing fine',
                                     epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Tutorial Name
    parser.add_argument(
        '--tutorial', '-t',
        action='store',
        required=True,
        help='name of the tutorial markdown file',
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    t = CheckTutorial()
    base_path = os.path.split(os.path.realpath(__file__))
    base_path = os.path.split(base_path[0])
    base_path = os.path.join(base_path[0], DOCUMENT_FOLDER_NAME)
    fname = os.path.join(base_path, args.tutorial)
    t.prepare_tutorial(fname)
    t.execute_all_tutorial_commands()
    return t.print_tutorial_summary()

if __name__ == "__main__":
    main()
