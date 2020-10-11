# -*- coding: utf-8 -*-

__author__ = "Paul Blottiere"
__contact__ = "blottiere.paul@gmail.com"
__copyright__ = "Copyright 2020, Paul Blottiere"
__date__ = "2020/10/10"
__email__ = "blottiere.paul@gmail.com"
__license__ = "GPLv3"

import subprocess
from sys import platform


if platform == "win32":
    deps = ["numpy", "scipy", "gdal", "scikit-learn"]

    for dep in deps:
        missing = []
        try:
            importlib.import_module(dep)
        except ModuleNotFoundError:
            missing.append(dep)

    p = subprocess.Popen(
        "cmd.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    cmds = [b"py3_env"]
    for dep in missing:
        c = "python3 -m pip install {} --user \n".format(dep)
        cmds.append(c.encode("latin1"))

    for cmd in cmds:
        p.stdin.write(cmd)

    p.stdin.close()
