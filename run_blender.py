import os
from pathlib import Path
import subprocess


def main():
    env = os.environ
    env.update({"PYTHONPATH": str(Path(".venv/Lib/site-packages").absolute())})
    env.update({"BLENDER_USER_SCRIPTS": str(Path("scripts").absolute())})
    subprocess.call([str(Path("blender/blender.exe").absolute()), "--python-use-system-env"], env=env)


if __name__ == "__main__":
    main()
