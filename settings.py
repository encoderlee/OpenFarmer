from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Settings:
    path_logs: str
    chrome_data_dir: str
    url_db: str = None
    # 发送http请求的间隔
    req_interval = 3
    # 发送合约请求的间隔（在http请求的间隔基础上再加几秒）
    transact_interval = 3
    # 每小时至少扫描一次，即使没有可用的作物，这样可以处理上次扫码后新种的作物
    max_scan_interval = timedelta(minutes=15)
    # 每次扫描至少间隔10秒，哪怕是出错重扫
    min_scan_interval = timedelta(seconds=10)


# 用户配置参数
class user_param:
    wax_account: str = None
    use_proxy: str = True
    proxy: str = None

    build: bool = True
    mining: bool = True
    chicken: bool = True
    plant: bool = True
    cow: bool = True
    mbs: bool = True
    withdraw: bool = True
    auto_deposit: bool = True
    sell_corn: bool = True
    sell_barley: bool = True
    sell_milk: bool = True
    sell_egg: bool = True
    auto_plant: bool = True
    # 能量不够的时候，就去恢复那么多能量,但不超过最大能量
    recover_energy: int = 500
    min_energy: int = 50

    on_server: bool = False

    # 账号中剩余多少材料不提现
    need_fww: int = 200
    need_fwf: int = 200
    need_fwg: int = 200
    # 最少提现数量，3种材料总和
    withdraw_min: int = 200

    remaining_corn_num: int = 0
    remaining_barley_num: int = 0
    remaining_milk_num: int = 0
    remaining_egg_num: int = 0

    barleyseed_num: int = 0
    cornseed_num: int = 0

    fww_min: int = 0
    deposit_fww: int = 0
    fwf_min: int = 0
    deposit_fwf: int = 0
    fwg_min: int = 0
    deposit_fwg: int = 0

    min_durability: int = 0


def load_user_param(user: dict):
    user_param.wax_account = user["wax_account"]
    user_param.use_proxy = user.get("proxy", True)
    user_param.proxy = user.get("proxy", None)
    user_param.build = user.get("build", True)
    user_param.mining = user.get("mining", True)
    user_param.chicken = user.get("chicken", True)
    user_param.cow = user.get("cow", True)
    user_param.plant = user.get("plant", True)
    user_param.mbs = user.get("mbs", True)
    user_param.sell_corn = user.get("sell_corn", True)
    user_param.sell_barley = user.get("sell_barley", True)
    user_param.sell_milk = user.get("sell_milk", True)
    user_param.sell_egg = user.get("sell_egg", True)
    user_param.auto_plant = user.get("auto_plant", True)
    user_param.recover_energy = user.get("recover_energy", 500)
    user_param.min_energy = user.get("min_energy", 50)
    user_param.min_durability = user.get("min_durability", 0)
    user_param.withdraw = user.get("withdraw", True)
    user_param.auto_deposit = user.get("auto_deposit", True)
    user_param.need_fww = user.get("need_fww", 200)
    user_param.need_fwf = user.get("need_fwf", 200)
    user_param.need_fwg = user.get("need_fwg", 200)
    user_param.withdraw_min = user.get("withdraw_min", 200)
    user_param.remaining_corn_num = user.get("remaining_corn_num", 0)
    user_param.remaining_barley_num = user.get("remaining_barley_num", 0)
    user_param.remaining_milk_num = user.get("remaining_milk_num", 0)
    user_param.remaining_egg_num = user.get("remaining_egg_num", 0)

    user_param.barleyseed_num = user.get("barleyseed_num", 0)
    user_param.cornseed_num = user.get("cornseed_num", 0)

    user_param.fww_min = user.get("fww_min", 0)
    user_param.deposit_fww = user.get("deposit_fww", 0)
    user_param.fwf_min = user.get("fwf_min", 0)
    user_param.deposit_fwf = user.get("deposit_fwf", 0)
    user_param.fwg_min = user.get("fwg_min", 0)
    user_param.deposit_fwg = user.get("deposit_fwg", 0)


cfg = Settings(
    path_logs="./logs/",
    chrome_data_dir="./data_dir/",
)
