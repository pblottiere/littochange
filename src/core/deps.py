# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import importlib
import subprocess
from sys import platform


class Deps(object):

    def run(self):
        if platform != "win32":
            return

        deps = ["numpy", "scipy", "gdal", "scikit-learn"]

        missing = []
        for dep in deps:
            try:
                if dep == "scikit-learn":
                    dep = "sklearn"
                importlib.import_module(dep)
            except ModuleNotFoundError:
                if dep == "sklearn":
                    dep = "scikit-learn"
                missing.append(dep)

        if not missing:
            return None

        cmds = [b"py3_env\n"]
        for dep in missing:
            c = "python3 -m pip install {} --user \n".format(dep)
            cmds.append(c.encode("latin1"))

        p = subprocess.Popen(
            "cmd.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        for cmd in cmds:
            p.stdin.write(cmd)

        p.stdin.close()

        return missing
