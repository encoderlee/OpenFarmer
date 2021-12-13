# 游戏里的各种数据结构
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, ClassVar, Dict
import utils


farming_table = {}

# nft template_id
class NFT:
    Barley: int = 318606
    Corn: int = 318607
    Chicken: int = 298614
    Chick: int = 298613
    ChickenEgg: int = 298612
    Bull: int = 298611
    DairyCow: int = 298607
    Cow: int = 298603
    Calf: int = 298600
    CornSeed: int = 298596
    BarleySeed: int = 298595


# 金、木、食物、能量
@dataclass(init=False)
class Resoure:
    energy: Decimal = None
    max_energy: Decimal = None
    gold: Decimal = None
    wood: Decimal = None
    food: Decimal = None


@dataclass(init=False)
class Token:
    fwg: Decimal = None
    fww: Decimal = None
    fwf: Decimal = None


# 可操作的作物
@dataclass(init=False)
class Farming:
    asset_id: str = None
    name: str = None
    template_id: int = None
    next_availability: datetime = None

    def show(self, more=True) -> str:
        if more:
            return f"[{self.name}] [{self.asset_id}] [可操作时间:{utils.show_time(self.next_availability)}]"
        else:
            return f"[{self.name}] [{self.asset_id}]"


# 动物
@dataclass(init=False)
class Animal(Farming):
    times_claimed: int = None
    last_claimed: datetime = None
    day_claims_at: List[datetime] = None


# 大鸡
@dataclass(init=False)
class Chicken(Animal):
    energy_consumed: int = 0


####################################################### Crop #######################################################

# 农作物，大麦，玉米
@dataclass(init=False)
class Crop(Farming):
    times_claimed: int = None
    last_claimed: datetime = None

    # 最大耕作次数
    required_claims: int = None
    # 能量消耗
    energy_consumed: int = None
    # 浇水间隔
    charge_time: timedelta = None

    def show(self, more=True) -> str:
        if more:
            return f"[{self.name}] [{self.asset_id}] [耕作次数{self.times_claimed}/{self.required_claims}] [可操作时间:{utils.show_time(self.next_availability)}]"
        else:
            return f"[{self.name}] [{self.asset_id}]"


# 大麦
@dataclass(init=False)
class BarleySeed(Crop):
    name: str = "Barley Seed"
    template_id: int = 298595


# 玉米
@dataclass(init=False)
class CornSeed(Crop):
    name: str = "Corn Seed"
    template_id: int = 298596


supported_crops = [BarleySeed, CornSeed]

farming_table.update({cls.template_id: cls for cls in supported_crops})


def init_crop_config(rows: List[dict]):
    for item in rows:
        crop_class : Crop = farming_table.get(item["template_id"], None)
        if crop_class:
            crop_class.name = item["name"]
            crop_class.charge_time = timedelta(seconds=item["charge_time"])
            crop_class.energy_consumed = item["energy_consumed"]
            crop_class.required_claims = item["required_claims"]


# 从json构造农作物对象
def create_crop(item: dict) -> Crop:
    crop_class = farming_table.get(item["template_id"], None)
    if not crop_class:
        return None
    crop = crop_class()
    crop.asset_id = item["asset_id"]
    crop.name = item["name"]
    crop.times_claimed = item.get("times_claimed", None)
    crop.last_claimed = datetime.fromtimestamp(item["last_claimed"])
    crop.next_availability = datetime.fromtimestamp(item["next_availability"])
    return crop


####################################################### Tool #######################################################

# 工具
@dataclass(init=False)
class Tool(Farming):
    # 当前耐久
    current_durability: Decimal = None
    # 最大耐久
    durability: Decimal = None

    # 产出资源类型
    mining_type: str = None
    # 挖矿间隔
    charge_time: timedelta = None
    # 能量消耗
    energy_consumed: int = None
    # 耐久消耗
    durability_consumed: int = None

    def show(self, more=True) -> str:
        if more:
            return f"[{self.name}] [{self.asset_id}] [耐久度{self.current_durability}/{self.durability}] [可操作时间:{utils.show_time(self.next_availability)}]"
        else:
            return f"[{self.name}] [{self.asset_id}]"


# 斧头
@dataclass(init=False)
class Axe(Tool):
    name: str = "Axe"
    template_id: int = 203881


# 石斧
@dataclass(init=False)
class StoneAxe(Tool):
    name: str = "Stone Axe"
    template_id: int = 260763


# 古代石斧
@dataclass(init=False)
class AncientStoneAxe(Tool):
    name: str = "Ancient Stone Axe"
    template_id: int = 378691


# 锯子
@dataclass(init=False)
class Saw(Tool):
    name: str = "Saw"
    template_id: int = 203883


# 电锯
@dataclass(init=False)
class Chainsaw(Tool):
    name: str = "Chainsaw"
    template_id: int = 203886


# 钓鱼竿
@dataclass(init=False)
class FishingRod(Tool):
    name: str = "Fishing Rod"
    template_id: int = 203887


# 渔网
@dataclass(init=False)
class FishingNet(Tool):
    name: str = "Fishing Net"
    template_id: int = 203888


# 渔船
@dataclass(init=False)
class FishingBoat(Tool):
    name: str = "Fishing Boat"
    template_id: int = 203889


# 挖掘机
@dataclass(init=False)
class MiningExcavator(Tool):
    name: str = "Mining Excavator"
    template_id: int = 203891


supported_tools = [Axe, StoneAxe, AncientStoneAxe, Saw, Chainsaw, FishingRod, FishingNet, FishingBoat, MiningExcavator]

farming_table.update({cls.template_id: cls for cls in supported_tools})


def init_tool_config(rows: List[dict]):
    for item in rows:
        tool_class = farming_table.get(item["template_id"], None)
        if tool_class:
            tool_class.mining_type = item["type"]
            tool_class.charge_time = timedelta(seconds=item["charged_time"])
            tool_class.energy_consumed = item["energy_consumed"]
            tool_class.durability_consumed = item["durability_consumed"]

# 从json构造工具对象
def create_tool(item: dict) -> Tool:
    tool_class = farming_table.get(item["template_id"], None)
    if not tool_class:
        return None
    tool = tool_class()
    tool.asset_id = item["asset_id"]
    tool.next_availability = datetime.fromtimestamp(item["next_availability"])
    tool.current_durability = item["current_durability"]
    tool.durability = item["durability"]
    return tool


####################################################### Tool #######################################################

####################################################### MBS  #######################################################

# 会员卡
@dataclass(init=False)
class MBS(Farming):
    energy_consumed: int = 100

    def __init__(self, template_id, name, type):
        self.name = name
        self.template_id = template_id
        self.type = type

    def show(self, more=True) -> str:
        if more:
            return f"[{self.name}] [类型:{self.type}] [asset_id:{self.asset_id}] [可操作时间:{utils.show_time(self.next_availability)}]"
        else:
            return f"[{self.name}] [类型:{self.type}]"

mbs_table : Dict[int, MBS]= {}


def init_mbs_config(rows: List[dict]):
    for item in rows:
        mbs = MBS(item["template_id"], item["name"], item["type"])
        mbs_table[item["template_id"]] = mbs

# 从json构造mbs对象
def create_mbs(item: dict) -> MBS:
    mbs_class = mbs_table.get(item["template_id"], None)
    if not mbs_class:
        return None
    mbs = MBS(mbs_class.template_id, mbs_class.name, mbs_class.type)
    mbs.asset_id = item["asset_id"]
    mbs.next_availability = datetime.fromtimestamp(item["next_availability"])
    return mbs

####################################################### MBS #######################################################


# 建筑物
@dataclass(init=False)
class Building(Farming):
    # 能量消耗
    energy_consumed: int = 200
    times_claimed: int = None
    last_claimed: datetime = None
    is_ready: int = None


# NFT资产，可以是小麦，小麦种子，牛奶等
@dataclass(init=False)
class Asset:
    asset_id: str
    name: str
    is_transferable: bool
    is_burnable: bool
    schema_name: str
    template_id: str


# 从http返回的json数据构造对象
def create_farming(item: dict) -> Farming:
    template_id = item["template_id"]
    if template_id == NFT.CornSeed:
        fm = CornSeed()
    elif template_id == NFT.BarleySeed:
        fm = BarleySeed()
    elif template_id == NFT.Chicken:
        fm = Chicken()
        fm.day_claims_at = [datetime.fromtimestamp(item) for item in item["day_claims_at"]]
    else:
        raise Exception("尚未支持的作物类型:{0}".format(item))
    fm.asset_id = item["asset_id"]
    fm.name = item["name"]
    fm.template_id = template_id
    fm.times_claimed = item.get("times_claimed", None)
    fm.last_claimed = datetime.fromtimestamp(item["last_claimed"])
    fm.next_availability = datetime.fromtimestamp(item["next_availability"])
    return fm
