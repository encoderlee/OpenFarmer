#!/usr/bin/python3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import tenacity
from tenacity import stop_after_attempt, wait_fixed, retry_if_exception_type, RetryCallState
import logging
import requests
from requests.exceptions import RequestException
import functools
from decimal import Decimal
from typing import List, Dict
import base64
from pprint import pprint
import logger
import utils
from utils import plat
from settings import user_param
import res
from res import Building, Resoure, Animal, Asset, Farming, Crop, NFT, Axe, Tool, Token, Chicken, FishingRod, MBS
from datetime import datetime, timedelta
from settings import cfg
import os
from logger import log

class FarmerException(Exception):
    pass


class CookieExpireException(FarmerException):
    pass


# 调用智能合约出错，此时应停止并检查日志，不宜反复重试
class TransactException(FarmerException):
    # 有的智能合约错误可以重试,-1为无限重试
    def __init__(self, msg, retry=True, max_retry_times: int = -1):
        super().__init__(msg)
        self.retry = retry
        self.max_retry_times = max_retry_times


# 遇到不可恢复的错误 ,终止程序
class StopException(FarmerException):
    pass


class Status:
    Continue = 1
    Stop = 2


class Farmer:
    # wax rpc
    # url_rpc = "https://api.wax.alohaeos.com/v1/chain/"
    url_rpc = "https://wax.pink.gg/v1/chain/"
    url_table_row = url_rpc + "get_table_rows"
    # 资产API
    url_assets = "https://wax.api.atomicassets.io/atomicassets/v1/assets"
    waxjs: str = None
    myjs: str = None
    chrome_data_dir = os.path.abspath(cfg.chrome_data_dir)

    def __init__(self):
        self.wax_account: str = None
        self.login_name: str = None
        self.password: str = None
        self.driver: webdriver.Chrome = None
        self.proxy: str = None
        self.http: requests.Session = None
        self.cookies: List[dict] = None
        self.log: logging.LoggerAdapter = log
        # 下一次可以操作东西的时间
        self.next_operate_time: datetime = datetime.max
        # 下一次扫描时间
        self.next_scan_time: datetime = datetime.min
        # 本轮扫描中暂不可操作的东西
        self.not_operational: List[Farming] = []
        # 智能合约连续出错次数
        self.count_error_transact = 0
        # 本轮扫描中作物操作成功个数
        self.count_success_claim = 0
        # 本轮扫描中作物操作失败个数
        self.count_error_claim = 0
        # 本轮开始时的资源数量
        self.resoure: Resoure = None
        self.token: Token = None

    def close(self):
        if self.driver:
            self.log.info("稍等，程序正在退出")
            self.driver.quit()

    def init(self):
        self.log.extra["tag"] = self.wax_account
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        data_dir = os.path.join(Farmer.chrome_data_dir, self.wax_account)
        options.add_argument("--user-data-dir={0}".format(data_dir))
        if self.proxy:
            options.add_argument("--proxy-server={0}".format(self.proxy))
        self.driver = webdriver.Chrome(plat.driver_path, options=options)
        self.driver.implicitly_wait(60)
        self.driver.set_script_timeout(60)
        self.http = requests.Session()
        self.http.trust_env = False
        self.http.request = functools.partial(self.http.request, timeout=30)
        if self.proxy:
            self.http.proxies = {
                "http": "http://{0}".format(self.proxy),
                "https": "http://{0}".format(self.proxy),
            }
        http_retry_wrapper = tenacity.retry(wait=wait_fixed(cfg.req_interval), stop=stop_after_attempt(5),
                                            retry=retry_if_exception_type(RequestException),
                                            before_sleep=self.log_retry, reraise=True)
        self.http.get = http_retry_wrapper(self.http.get)
        self.http.post = http_retry_wrapper(self.http.post)

    def inject_waxjs(self):
        # 如果已经注入过就不再注入了
        if self.driver.execute_script("return window.mywax != undefined;"):
            return True

        if not Farmer.waxjs:
            with open("waxjs.js", "r") as file:
                Farmer.waxjs = file.read()
                file.close()
                Farmer.waxjs = base64.b64encode(Farmer.waxjs.encode()).decode()
        if not Farmer.myjs:
            with open("inject.js", "r") as file:
                Farmer.myjs = file.read()
                file.close()

        code = "var s = document.createElement('script');"
        code += "s.type = 'text/javascript';"
        code += "s.text = atob('{0}');".format(Farmer.waxjs)
        code += "document.head.appendChild(s);"
        self.driver.execute_script(code)
        self.driver.execute_script(Farmer.myjs)
        return True

    def start(self):
        self.log.info("启动浏览器")
        if self.cookies:
            self.log.info("使用预设的cookie自动登录")
            cookies = self.cookies["cookies"]
            key_cookie = {}
            for item in cookies:
                if item.get("domain") == "all-access.wax.io":
                    key_cookie = item
                    break
            if not key_cookie:
                raise CookieExpireException("not find cookie domain as all-access.wax.io")
            ret = self.driver.execute_cdp_cmd("Network.setCookie", key_cookie)
            self.log.info("Network.setCookie: {0}".format(ret))
            if not ret["success"]:
                raise CookieExpireException("Network.setCookie error")
        self.driver.get("https://play.farmersworld.io/")
        # 等待页面加载完毕
        elem = self.driver.find_element(By.ID, "RPC-Endpoint")
        elem.find_element(By.XPATH, "option[contains(@name, 'https')]")
        wait_seconds = 60
        if self.may_cache_login():
            self.log.info("使用Cache自动登录")
        else:
            wait_seconds = 600
            self.log.info("请在弹出的窗口中手动登录账号")
        # 点击登录按钮，点击WAX云钱包方式登录
        elem = self.driver.find_element(By.CLASS_NAME, "login-button")
        elem.click()
        elem = self.driver.find_element(By.CLASS_NAME, "login-button--text")
        elem.click()
        # 等待登录成功
        self.log.info("等待登录")
        WebDriverWait(self.driver, wait_seconds, 1).until(
            EC.presence_of_element_located((By.XPATH, "//img[@class='navbar-group--icon' and @alt='Map']")))
        # self.driver.find_element(By.XPATH, "//img[@class='navbar-group--icon' and @alt='Map']")
        self.log.info("登录成功,稍等...")
        time.sleep(cfg.req_interval)
        self.inject_waxjs()
        ret = self.driver.execute_script("return window.wax_login();")
        self.log.info("window.wax_login(): {0}".format(ret))
        if not ret[0]:
            raise CookieExpireException("cookie失效")

        # 从服务器获取游戏参数
        self.log.info("正在加载游戏配置")
        self.init_farming_config()
        time.sleep(cfg.req_interval)

    def may_cache_login(self):
        cookies = self.driver.execute_cdp_cmd("Network.getCookies", {"urls": ["https://all-access.wax.io"]})
        for item in cookies["cookies"]:
            if item.get("name") == "token_id":
                return True
        return False

    def log_retry(self, state: RetryCallState):
        exp = state.outcome.exception()
        if isinstance(exp, RequestException):
            self.log.info("网络错误: {0}".format(exp))
            self.log.info("正在重试: [{0}]".format(state.attempt_number))

    def table_row_template(self) -> dict:
        post_data = {
            "json": True,
            "code": "farmersworld",
            "scope": "farmersworld",
            "table": None,  # 覆写
            "lower_bound": self.wax_account,
            "upper_bound": self.wax_account,
            "index_position": None,  # 覆写
            "key_type": "i64",
            "limit": 100,
            "reverse": False,
            "show_payer": False
        }
        return post_data

    # 从服务器获取各种工具和作物的参数
    def init_farming_config(self):
        # 工具
        post_data = {
            "json": True,
            "code": "farmersworld",
            "scope": "farmersworld",
            "table": "toolconfs",
            "lower_bound": "",
            "upper_bound": "",
            "index_position": 1,
            "key_type": "",
            "limit": 100,
            "reverse": False,
            "show_payer": False
        }
        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get tools config:{0}".format(resp.text))
        resp = resp.json()
        res.init_tool_config(resp["rows"])
        time.sleep(cfg.req_interval)

        # 农作物
        post_data["table"] = "cropconf"
        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get crop config:{0}".format(resp.text))
        resp = resp.json()
        res.init_crop_config(resp["rows"])

        # 会员卡
        post_data["table"] = "mbsconf"
        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get mbs config:{0}".format(resp.text))
        resp = resp.json()
        res.init_mbs_config(resp["rows"])

    # 获取游戏中的三种资源数量和能量值
    def get_resource(self) -> Resoure:
        post_data = self.table_row_template()
        post_data["table"] = "accounts"
        post_data["index_position"] = 1

        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get_table_rows:{0}".format(resp.text))
        resp = resp.json()
        resource = Resoure()
        resource.energy = Decimal(resp["rows"][0]["energy"])
        resource.max_energy = Decimal(resp["rows"][0]["max_energy"])
        balances: List[str] = resp["rows"][0]["balances"]
        for item in balances:
            sp = item.split(" ")
            if sp[1].upper() == "GOLD":
                resource.gold = Decimal(sp[0])
            elif sp[1].upper() == "WOOD":
                resource.wood = Decimal(sp[0])
            elif sp[1].upper() == "FOOD":
                resource.food = Decimal(sp[0])
        self.log.debug("resource: {0}".format(resource))
        return resource

    # 获取建造信息
    def get_buildings(self) -> List[Building]:
        post_data = self.table_row_template()
        post_data["table"] = "buildings"
        post_data["index_position"] = 2

        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get_buildings_info:{0}".format(resp.text))
        resp = resp.json()
        buildings = []
        for item in resp["rows"]:
            build = Building()
            build.asset_id = item["asset_id"]
            build.name = item["name"]
            build.is_ready = item["is_ready"]
            build.next_availability = datetime.fromtimestamp(item["next_availability"])
            build.template_id = item["template_id"]
            build.times_claimed = item.get("times_claimed", None)
            if build.is_ready == 1:
                continue
            buildings.append(build)
        return buildings

    # 获取农作物信息
    def get_crops(self) -> List[Crop]:
        post_data = self.table_row_template()
        post_data["table"] = "crops"
        post_data["index_position"] = 2

        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get_crops_info:{0}".format(resp.text))
        resp = resp.json()
        crops = []
        for item in resp["rows"]:
            crop = res.create_crop(item)
            if crop:
                crops.append(crop)
            else:
                self.log.warning("尚未支持的农作物类型:{0}".format(item))
        return crops

    # claim 建筑
    def claim_building(self, item: Building):
        self.consume_energy(Decimal(item.energy_consumed))
        transaction = {
            "actions": [{
                "account": "farmersworld",
                "name": "bldclaim",
                "authorization": [{
                    "actor": self.wax_account,
                    "permission": "active",
                }],
                "data": {
                    "asset_id": item.asset_id,
                    "owner": self.wax_account,
                },
            }],
        }
        return self.wax_transact(transaction)

    # 耕种农作物
    def claim_crop(self, crop: Crop):
        energy_consumed = crop.energy_consumed
        fake_consumed = Decimal(0)
        if crop.times_claimed == crop.required_claims - 1:
            # 收获前的最后一次耕作，多需要200点能量，游戏合约BUG
            fake_consumed = Decimal(200)
        self.consume_energy(Decimal(energy_consumed), fake_consumed)
        transaction = {
            "actions": [{
                "account": "farmersworld",
                "name": "cropclaim",
                "authorization": [{
                    "actor": self.wax_account,
                    "permission": "active",
                }],
                "data": {
                    "crop_id": crop.asset_id,
                    "owner": self.wax_account,
                },
            }],
        }
        return self.wax_transact(transaction)

    def claim_buildings(self, blds: List[Building]):
        for item in blds:
            self.log.info("正在建造: {0}".format(item.show()))
            if self.claim_building(item):
                self.log.info("建造成功: {0}".format(item.show(more=False)))
            else:
                self.log.info("建造失败: {0}".format(item.show(more=False)))
                self.count_error_claim += 1
            time.sleep(cfg.req_interval)

    def claim_crops(self, crops: List[Crop]):
        for item in crops:
            self.log.info("正在耕作: {0}".format(item.show()))
            if self.claim_crop(item):
                self.log.info("耕作成功: {0}".format(item.show(more=False)))
            else:
                self.log.info("耕作失败: {0}".format(item.show(more=False)))
                self.count_error_claim += 1
            time.sleep(cfg.req_interval)

    # 获取箱子里的NTF
    def get_chest(self) -> dict:
        payload = {
            "limit": 1000,
            "collection_name": "farmersworld",
            "owner": self.wax_account,
            "template_blacklist": "260676",
        }
        resp = self.http.get(self.url_assets, params=payload)
        self.log.debug("get_chest:{0}".format(resp.text))
        resp = resp.json()
        assert resp["success"]
        return resp

    # schema: [foods]
    def get_chest_by_schema_name(self, schema_name: str):
        payload = {
            "limit": 1000,
            "collection_name": "farmersworld",
            "owner": self.wax_account,
            "schema_name": schema_name,
        }
        resp = self.http.get(self.url_assets, params=payload)
        self.log.debug("get_chest_by_schema_name:{0}".format(resp.text))
        resp = resp.json()
        assert resp["success"]
        return resp

    # template_id: [大麦 318606]
    def get_chest_by_template_id(self, template_id: int):
        payload = {
            "limit": 1000,
            "collection_name": "farmersworld",
            "owner": self.wax_account,
            "template_id": template_id,
        }
        resp = self.http.get(self.url_assets, params=payload)
        self.log.debug("get_chest_by_schema_name:{0}".format(resp.text))
        resp = resp.json()
        assert resp["success"]
        return resp

    # 获取大麦
    def get_barley(self) -> List[Asset]:
        barley_list = []
        chest = self.get_chest_by_template_id(NFT.Barley)
        if len(chest["data"]) <= 0:
            return barley_list
        for item in chest["data"]:
            assert item["name"] == "Barley"
            asset = Asset()
            asset.asset_id = item["asset_id"]
            asset.name = item["name"]
            asset.is_transferable = item["is_transferable"]
            asset.is_burnable = item["is_transferable"]
            asset.schema_name = item["schema"]["schema_name"]
            asset.template_id = item["template"]["template_id"]
            barley_list.append(asset)
        self.log.info("get_barley: {0}".format(barley_list))
        return barley_list

    # 获取鸡的信息
    def get_chicken(self) -> List[Animal]:
        post_data = self.table_row_template()
        post_data["table"] = "animals"
        post_data["index_position"] = 2

        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get_chicken_info:{0}".format(resp.text))
        resp = resp.json()
        animals = []
        for item in resp["rows"]:
            if item["name"] != "Chicken":
                continue
            anim: Chicken = res.create_farming(item)
            animals.append(anim)
        return animals

    # 喂鸡
    def feed_chicken(self, asset_id_food: str, chicken: Chicken) -> bool:
        self.log.info("feed [{0}] to [{1}]".format(asset_id_food, chicken.asset_id))
        self.consume_energy(Decimal(chicken.energy_consumed))
        transaction = {
            "actions": [{
                "account": "atomicassets",
                "name": "transfer",
                "authorization": [{
                    "actor": self.wax_account,
                    "permission": "active",
                }],
                "data": {
                    "asset_ids": [asset_id_food],
                    "from": self.wax_account,
                    "memo": "feed_animal:{0}".format(chicken.asset_id),
                    "to": "farmersworld"
                },
            }],
        }
        return self.wax_transact(transaction)

    # 饲养鸡
    def claim_chicken(self, animals: List[Animal]):
        list_barley = self.get_barley()
        self.log.info("剩余大麦数量: {0}".format(len(list_barley)))
        for item in animals:
            if len(list_barley) <= 0:
                self.log.warning("大麦数量不足,请及时补充")
                return False
            barley = list_barley.pop()
            self.log.info("正在喂鸡: {0}".format(item.show()))
            success = self.feed_chicken(barley.asset_id, item)
            if success:
                self.log.info("喂鸡成功: {0}".format(item.show(more=False)))
            else:
                self.log.info("喂鸡失败: {0}".format(item.show(more=False)))
                self.count_error_claim += 1
            time.sleep(cfg.req_interval)
        return True

    # 获取wax账户信息
    def wax_get_account(self):
        url = self.url_rpc + "get_account"
        post_data = {"account_name": self.wax_account}
        resp = self.http.post(url, json=post_data)
        self.log.debug("get_account:{0}".format(resp.text))
        resp = resp.json()
        return resp

    # 获取三种资源的代币余额 FWF FWG FWW
    def get_fw_balance(self) -> Token:
        url = self.url_rpc + "get_currency_balance"
        post_data = {
            "code": "farmerstoken",
            "account": self.wax_account,
            "symbol": None
        }
        resp = self.http.post(url, json=post_data)

        self.log.debug("get_fw_balance:{0}".format(resp.text))
        resp = resp.json()
        balance = Token()
        for item in resp:
            sp = item.split(" ")
            if sp[1].upper() == "FWF":
                balance.fwf = Decimal(sp[0])
            elif sp[1].upper() == "FWG":
                balance.fwg = Decimal(sp[0])
            elif sp[1].upper() == "FWW":
                balance.fww = Decimal(sp[0])
        self.log.debug("fw_balance: {0}".format(balance))
        return balance

    # 签署交易(只许成功，否则抛异常）
    def wax_transact(self, transaction: dict):
        self.inject_waxjs()
        self.log.info("begin transact: {0}".format(transaction))
        try:
            success, result = self.driver.execute_script("return window.wax_transact(arguments[0]);", transaction)
            if success:
                self.log.info("transact ok, transaction_id: [{0}]".format(result["transaction_id"]))
                self.log.debug("transact result: {0}".format(result))
                return True
            else:
                self.log.error("transact error: {0}".format(result))
                if "is greater than the maximum billable" in result:
                    self.log.error("EOS CPU资源不足，可能需要质押更多WAX，一般为误报，稍后重试")
                    raise TransactException(result)
                raise TransactException(result)
        except WebDriverException as e:
            self.log.error("transact error: {0}".format(e))
            self.log.exception(str(e))
            raise TransactException(result)

    # 过滤可操作的作物
    def filter_operable(self, items: List[Farming]) -> Farming:
        now = datetime.now()
        op = []
        for item in items:
            if isinstance(item, Building):
                if item.is_ready == 1:
                    continue
            # 鸡24小时内最多喂4次
            if isinstance(item, Chicken):
                if len(item.day_claims_at) >= 4:
                    next_op_time = item.day_claims_at[0] + timedelta(hours=24)
                    item.next_availability = max(item.next_availability, next_op_time)
            if now < item.next_availability:
                self.not_operational.append(item)
                continue
            op.append(item)
        return op

    def scan_buildings(self):
        self.log.info("检查建筑物")
        buildings = self.get_buildings()
        if not buildings:
            self.log.info("没有未完成的建筑物")
            return True
        self.log.info("未完成的建筑物:")
        for item in buildings:
            self.log.info(item.show())
        buildings = self.filter_operable(buildings)
        if not buildings:
            self.log.info("没有可操作的建筑物")
            return True
        self.log.info("可操作的建筑物:")
        for item in buildings:
            self.log.info(item.show())
        self.claim_buildings(buildings)
        return True

    def scan_crops(self):
        self.log.info("检查农田")
        crops = self.get_crops()
        if not crops:
            self.log.info("没有农作物")
            return True
        self.log.info("种植的农作物:")
        for item in crops:
            self.log.info(item.show())
        crops = self.filter_operable(crops)
        if not crops:
            self.log.info("没有可操作的农作物")
            return True
        self.log.info("可操作的农作物:")
        for item in crops:
            self.log.info(item.show())
        self.claim_crops(crops)
        return True

    def scan_animals(self):
        self.log.info("检查农场")
        animals = self.get_chicken()
        self.log.info("饲养的动物:")
        for item in animals:
            self.log.info(item.show())
        animals = self.filter_operable(animals)
        if not animals:
            self.log.info("没有可操作的动物")
            return True
        self.log.info("可操作的动物:")
        for item in animals:
            self.log.info(item.show())
        self.claim_chicken(animals)
        return True

    def get_tools(self):
        post_data = self.table_row_template()
        post_data["table"] = "tools"
        post_data["index_position"] = 2

        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get_tools:{0}".format(resp.text))
        resp = resp.json()
        tools = []
        for item in resp["rows"]:
            tool = res.create_tool(item)
            if tool:
                tools.append(tool)
            else:
                self.log.warning("尚未支持的工具类型:{0}".format(item))
        return tools

    # 使用工具挖矿操作
    def claim_mining(self, tools: List[Tool]):
        for item in tools:
            self.log.info("正在采矿: {0}".format(item.show()))
            self.consume_energy(Decimal(item.energy_consumed))
            self.consume_durability(item)
            transaction = {
                "actions": [{
                    "account": "farmersworld",
                    "name": "claim",
                    "authorization": [{
                        "actor": self.wax_account,
                        "permission": "active",
                    }],
                    "data": {
                        "asset_id": item.asset_id,
                        "owner": self.wax_account,
                    },
                }],
            }
            self.wax_transact(transaction)
            self.log.info("采矿成功: {0}".format(item.show(more=False)))
            time.sleep(cfg.req_interval)

    def scan_mining(self):
        self.log.info("检查矿场")
        tools = self.get_tools()
        self.log.info("采矿的工具:")
        for item in tools:
            self.log.info(item.show())
        tools = self.filter_operable(tools)
        if not tools:
            self.log.info("没有可操作的采矿工具")
            return True
        self.log.info("可操作的采矿工具:")
        for item in tools:
            self.log.info(item.show())
        self.claim_mining(tools)
        return True

    # 修理工具
    def repair_tool(self, tool: Tool):
        self.log.info(f"正在修理工具: {tool.show()}")
        consume_gold = (tool.durability - tool.current_durability) // 5
        if Decimal(consume_gold) > self.resoure.gold:
            raise FarmerException("没有足够的金币修理工具，请补充金币，稍后程序自动重试")
        transaction = {
            "actions": [{
                "account": "farmersworld",
                "name": "repair",
                "authorization": [{
                    "actor": self.wax_account,
                    "permission": "active",
                }],
                "data": {
                    "asset_id": tool.asset_id,
                    "asset_owner": self.wax_account,
                },
            }],
        }
        self.wax_transact(transaction)
        self.log.info(f"修理完毕: {tool.show(more=False)}")

    # 恢复能量
    def recover_energy(self, count: Decimal):
        self.log.info("正在恢复能量: 【{0}】点 ".format(count))
        need_food = count // Decimal(5)
        if need_food > self.resoure.food:
            self.log.error(f"食物不足，仅剩【{self.resoure.food}】，兑换能量【{count}】点需要【{need_food}】个食物，请手工处理")
            raise FarmerException("没有足够的食物，请补充食物，稍后程序自动重试")

        transaction = {
            "actions": [{
                "account": "farmersworld",
                "name": "recover",
                "authorization": [{
                    "actor": self.wax_account,
                    "permission": "active",
                }],
                "data": {
                    "energy_recovered": int(count),
                    "owner": self.wax_account,
                },
            }],
        }
        return self.wax_transact(transaction)

    # 消耗能量 （操作前模拟计算）
    def consume_energy(self, real_consume: Decimal, fake_consume: Decimal = Decimal(0)):
        consume = real_consume + fake_consume
        if self.resoure.energy - consume > 0:
            self.resoure.energy -= real_consume
            return True
        else:
            self.log.info("能量不足")
            recover = min(user_param.recover_energy, self.resoure.max_energy - self.resoure.energy)
            recover = (recover // Decimal(5)) * Decimal(5)
            self.recover_energy(recover)
            self.resoure.energy += recover
            self.resoure.energy -= real_consume
            return True

    # 消耗耐久度 （操作前模拟计算）
    def consume_durability(self, tool: Tool):
        if tool.current_durability >= tool.durability_consumed:
            return True
        else:
            self.log.info("工具耐久不足")
            self.repair_tool(tool)


    def scan_mbs(self):
        self.log.info("检查会员卡")
        mbs = self.get_mbs()
        for item in mbs:
            self.log.info(item.show(True))

        mbs = self.filter_operable(mbs)
        if not mbs:
            self.log.info("没有可操作的会员卡")
            return True
        self.log.info("可操作的会员卡:")
        for item in mbs:
            self.log.info(item.show(True))
        self.claim_mbs(mbs)
        return True

    def get_mbs(self) -> List[MBS]:
        post_data = self.table_row_template()
        post_data["table"] = "mbs"
        post_data["index_position"] = 2
        post_data["key_type"] = "i64"

        resp = self.http.post(self.url_table_row, json=post_data)
        self.log.debug("get_mbs:{0}".format(resp.text))
        resp = resp.json()
        mbs = []
        for item in resp["rows"]:
            mb = res.create_mbs(item)
            if mb:
                mbs.append(mb)
            else:
                self.log.warning("尚未支持的会员卡类型:{0}".format(item))
        return mbs

    def claim_mbs(self, tools: List[MBS]):
        for item in tools:
            self.log.info("正在点击会员卡: {0}".format(item.show(True)))
            self.consume_energy(Decimal(item.energy_consumed))
            transaction = {
                "actions": [{
                    "account": "farmersworld",
                    "name": "mbsclaim",
                    "authorization": [{
                        "actor": self.wax_account,
                        "permission": "active",
                    }],
                    "data": {
                        "asset_id": item.asset_id,
                        "owner": self.wax_account,
                    },
                }],
            }
            self.wax_transact(transaction)
            self.log.info("点击会员卡成功: {0}".format(item.show(more=False)))
            time.sleep(cfg.req_interval)

    def scan_resource(self):
        r = self.get_resource()
        self.log.info(f"金币【{r.gold}】 木头【{r.wood}】 食物【{r.food}】 能量【{r.energy}/{r.max_energy}】")
        self.resoure = r
        time.sleep(cfg.req_interval)
        self.token = self.get_fw_balance()
        self.log.info(f"FWG【{self.token.fwg}】 FWW【{self.token.fww}】 FWF【{self.token.fwf}】")

    def reset_before_scan(self):
        self.not_operational.clear()
        self.count_success_claim = 0
        self.count_error_claim = 0

    # 检查正在培养的作物， 返回值：是否继续运行程序
    def scan_all(self) -> int:
        status = Status.Continue
        try:
            self.reset_before_scan()
            self.log.info("开始一轮扫描")
            self.scan_resource()
            time.sleep(cfg.req_interval)

            if user_param.mbs:
                self.scan_mbs()
                time.sleep(cfg.req_interval)
            if user_param.build:
                self.scan_buildings()
                time.sleep(cfg.req_interval)
            if user_param.plant:
                self.scan_crops()
                time.sleep(cfg.req_interval)
            if user_param.chicken:
                self.scan_animals()
                time.sleep(cfg.req_interval)
            if user_param.mining:
                self.scan_mining()
                time.sleep(cfg.req_interval)
            self.log.info("结束一轮扫描")
            if self.not_operational:
                self.next_operate_time = min([item.next_availability for item in self.not_operational])
                self.log.info("下一次可操作时间: {0}".format(utils.show_time(self.next_operate_time)))
                # 可操作时间到了，也要延后5秒再扫，以免
                self.next_operate_time += timedelta(seconds=5)
            else:
                self.next_operate_time = datetime.max
            if self.count_success_claim > 0 or self.count_error_claim > 0:
                self.log.info(f"本轮操作成功数量: {self.count_success_claim} 操作失败数量: {self.count_error_claim}")

            if self.count_error_claim > 0:
                self.log.info("本轮有失败操作，稍后重试")
                self.next_scan_time = datetime.now() + cfg.min_scan_interval
            else:
                self.next_scan_time = datetime.now() + cfg.max_scan_interval

            self.next_scan_time = min(self.next_scan_time, self.next_operate_time)

            # 没有合约出错，清空错误计数器
            self.count_error_transact = 0

        except TransactException as e:
            self.log.exception("智能合约调用出错")
            if not e.retry:
                return Status.Stop
            self.count_error_transact += 1
            self.log.error("合约调用异常【{0}】次".format(self.count_error_transact))
            if self.count_error_transact >= e.max_retry_times and e.max_retry_times != -1:
                self.log.error("合约连续调用异常")
                return Status.Stop
            self.next_scan_time = datetime.now() + cfg.min_scan_interval
        except CookieExpireException as e:
            self.log.exception(str(e))
            self.log.error("Cookie失效，请手动重启程序并重新登录")
            return Status.Stop
        except StopException as e:
            self.log.exception(str(e))
            self.log.error("不可恢复错误，请手动处理，然后重启程序并重新登录")
            return Status.Stop
        except FarmerException as e:
            self.log.exception(str(e))
            self.log.error("常规错误，稍后重试")
            self.next_scan_time = datetime.now() + cfg.min_scan_interval
        except Exception as e:
            self.log.exception(str(e))
            self.log.error("常规错误，稍后重试")
            self.next_scan_time = datetime.now() + cfg.min_scan_interval

        self.log.info("下一轮扫描时间: {0}".format(utils.show_time(self.next_scan_time)))
        return status

    def run_forever(self):
        while True:
            if datetime.now() > self.next_scan_time:
                status = self.scan_all()
                if status == Status.Stop:
                    self.close()
                    self.log.info("程序已停止，请检查日志后手动重启程序")
                    return 1
            time.sleep(1)



def test():
    pass


if __name__ == '__main__':
    test()
