# -*- coding: utf-8 -*-

import os
import subprocess


def execute(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
    try:
        out, err = proc.communicate()
    except TimeoutError:
        proc.kill()
        out, err = proc.communicate()
    return_code = proc.poll()
    if return_code != 0:
        raise CommandExecuteError(return_code, cmd, stderr=err, output=out)
    if out is None:
        out = ''
    return out.strip()


def find_tool(tool_name):
    detect_which()
    return execute(detect_which() + " " + tool_name)


def detect_which():
    cmd_which = "/usr/bin/which"
    if not os.path.exists(cmd_which):
        cmd_which = "/bin/which"
        if not os.path.exists(cmd_which):
            raise FileNotFoundError("ERROR: which command not found!")
    return cmd_which


class CommandExecuteError(subprocess.CalledProcessError):
    """ Extend CalledProcessError to support stderr parameter in 2.7 """

    def __init__(self, returncode, cmd, output=None, stderr=None):
        super(CommandExecuteError, self).__init__(returncode=returncode, cmd=cmd, output=output)
        self.stderr = stderr
