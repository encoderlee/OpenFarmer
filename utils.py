import psutil
from datetime import datetime
import platform
from typing import List
import shutil
import os

def show_time(t):
    if isinstance(t, datetime):
        return t.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')


class plat:
    name: str = None
    chromedriver: str = None
    python: str = None
    python_path: str = None
    driver_path:str =None


if platform.system().lower() == "windows":
    plat.name = "windows"
    plat.chromedriver = "chromedriver.exe"
    plat.python = "python.exe"
elif platform.system().lower() == "linux":
    plat.name = "linux"
    plat.chromedriver = "chromedriver"
    plat.python = "python3"
elif platform.system().lower() == "darwin":
    plat.name = "macos"
    plat.chromedriver = "chromedriver"
    plat.python = "python3"
plat.python_path = shutil.which(plat.python)
plat.driver_path = shutil.which(plat.chromedriver)
if not plat.driver_path:
    plat.driver_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], plat.chromedriver)

def kill_process_tree_by_id(pid: int):
    try:
        parent = psutil.Process(pid)
        process: List[psutil.Process] = parent.children(recursive=True)
        process.append(parent)
        for item in process:
            try:
                item.kill()
            except psutil.NoSuchProcess:
                pass
    except psutil.NoSuchProcess:
        pass


def kill_process_tree_by_name(name: str):
    for proc in psutil.process_iter():
        if proc.name() == name:
            kill_process_tree_by_id(proc.pid)


def all_webdriver() -> List[psutil.Process]:
    process = []
    for item in psutil.process_iter():
        if item.name() == plat.chromedriver:
            process.append(item)
    return process


def clear_all_webdriver():
    process = all_webdriver()
    for item in process:
        kill_process_tree_by_id(item.pid)


def clear_all_farmer():
    for item in psutil.process_iter():
        if item.name() == plat.python and "main.py" in item.cmdline():
            kill_process_tree_by_id(item.pid)
    clear_all_webdriver()


def clear_orphan_webdriver():
    process = all_webdriver()
    killed = []
    for item in process:
        if not item.parent():
            kill_process_tree_by_id(item.pid)
            killed.append(item)
        elif item.parent().name().lower() == "systemd":
            kill_process_tree_by_id(item.pid)
            killed.append(item)
    return killed


def test():
    proc_list = []
    for proc in psutil.process_iter():
        if "python.exe" in proc.name():
            proc_list.append(proc)
            print(proc.name())
            print(proc.cmdline())
            print(proc.exe())


if __name__ == '__main__':
    test()
    print(plat.python_path)
