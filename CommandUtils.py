# -*- coding: utf-8 -*-

import os
import subprocess


class CommandExecutor:

    _cmd_which = None

    @staticmethod
    def execute(cmd):
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).strip()

    @staticmethod
    def find_tool(tool_name):
        CommandExecutor._detect_which()
        return CommandExecutor.execute(CommandExecutor._cmd_which + " " + tool_name)

    @staticmethod
    def _detect_which():
        if CommandExecutor._cmd_which is not None:
            return CommandExecutor._cmd_which
        cmd_which = "/usr/bin/which"
        if not os.path.exists(cmd_which):
            cmd_which = "/bin/which"
            if not os.path.exists(cmd_which):
                raise FileNotFoundError("ERROR: which command not found!")
        CommandExecutor._cmd_which = cmd_which
