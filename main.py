#!/usr/bin/python3
from farmer import Farmer
import logger
from logger import log
import yaml
import sys
import utils
from settings import load_user_param, user_param

def run(config_file: str):
    with open(config_file, "r", encoding="utf8") as file:
        user: dict = yaml.load(file, Loader=yaml.FullLoader)
        file.close()
    load_user_param(user)
    logger.init_loger(user_param.wax_account)
    log.info("项目开源地址：https://github.com/lintan/OpenFarmer")
    log.info("WAX账号: {0}".format(user_param.wax_account))
    utils.clear_orphan_webdriver()
    farmer = Farmer()
    farmer.wax_account = user_param.wax_account
    if user_param.use_proxy:
        farmer.proxy = user_param.proxy
        log.info("use proxy: {0}".format(user_param.proxy))
    farmer.init()
    farmer.start()
    log.info("开始自动化，请勿刷新浏览器，如需手工操作建议新开一个浏览器操作")
    return farmer.run_forever()


def main():
    try:
        user_yml = "user.yml"
        if len(sys.argv) == 2:
            user_yml = sys.argv[1]
        run(user_yml)
    except Exception:
        log.exception("start error")
    input()


if __name__ == '__main__':
    main()
