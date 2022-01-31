# 游戏里的各种数据结构
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, ClassVar, Dict
import utils

farming_table = {}


# nft template_id
class NFT:
    Barley: int = 318606  # 大麦
    Corn: int = 318607  # 玉米
    Chicken: int = 298614  # 大鸡
    Chick: int = 298613  # 小鸡
    ChickenEgg: int = 298612  # 鸡蛋
    BabyCalf: int = 298597  # 小牛犊
    Calf: int = 298598  # 小牛
    FeMaleCalf: int = 298599  # 母小牛
    MaleCalf: int = 298600  # 公小牛
    Bull: int = 298611  # 公牛
    DairyCow: int = 298607  # 奶牛
    CornSeed: int = 298596  # 玉米种子
    BarleySeed: int = 298595  # 大麦种子
    Milk: int = 298593  # 牛奶


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


@dataclass(init=False)
class MbsSavedClaims:
    Wood: int = 0
    Food: int = 0
    Gold: int = 0


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


# ==== Food =====
# 牛奶
@dataclass(init=False)
class Milk(Farming):
    name: str = "Milk"
    template_id: int = 298593


# 玉米
@dataclass(init=False)
class Corn(Farming):
    name: str = "Corn"
    template_id: int = 318607
    golds_cost: int = 82


# 大麦
@dataclass(init=False)
class Barley(Farming):
    name: str = "Barley"
    template_id: int = 318606
    golds_cost: int = 55


supported_foods = [Milk, Corn, Barley]
farming_table.update({cls.template_id: cls for cls in supported_foods})


# ==== Food =====

# ################### Animal ######################

# 动物
@dataclass(init=False)
class Animal(Farming):
    # 能量消耗
    energy_consumed: int = None
    # 当前喂养次数
    times_claimed: int = None
    # 最大喂养次数
    required_claims: int = None
    # 最后喂养时间
    last_claimed: datetime = None
    # 喂养时间列表
    day_claims_at: List[datetime] = None
    # 间隔
    charge_time: timedelta = None
    # 24小时喂养次数
    daily_claim_limit: int = None
    # 消耗的nft
    consumed_card: int = None
    # 所属建筑
    required_building: int = None
    # 繁殖
    bearer_id: int = None
    partner_id: int = None

    def show(self, more=True, breeding=False) -> str:
        if more:
            if len(self.day_claims_at) >= self.daily_claim_limit:
                next_op_time = self.day_claims_at[0] + timedelta(hours=24)
                self.next_availability = max(self.next_availability, next_op_time)
            if not breeding:
                text = f"[{self.name}] [{self.asset_id}][24小时喂养次数{len(self.day_claims_at)}/{self.daily_claim_limit}] [喂养次数{self.times_claimed}/{self.required_claims}] [可操作时间:{utils.show_time(self.next_availability)}] "
            else:
                text = f"[{self.name}繁殖] [{self.bearer_id}][24小时喂养次数{len(self.day_claims_at)}/{self.daily_claim_limit}] [喂养次数{self.times_claimed}/{self.required_claims}] [可操作时间:{utils.show_time(self.next_availability)}] "
            return text
        else:
            return f"[{self.name}] [{self.asset_id}]"


# 大鸡
@dataclass(init=False)
class Chicken(Animal):
    name: str = "Chicken"
    template_id: int = 298614


# 小鸡
@dataclass(init=False)
class Chick(Animal):
    name: str = "Chick"
    template_id: int = 298613


# 小鸡
@dataclass(init=False)
class ChickenEgg(Animal):
    name: str = "ChickenEgg"
    template_id: int = 298612


# 小牛犊
@dataclass(init=False)
class BabyCalf(Animal):
    name: str = "BabyCalf"
    template_id: int = 298597


# 小牛
@dataclass(init=False)
class Calf(Animal):
    name: str = "Calf"
    template_id: int = 298598


# 母小牛
@dataclass(init=False)
class FeMaleCalf(Animal):
    name: str = "FeMaleCalf"
    template_id: int = 298599


# 公小牛
@dataclass(init=False)
class MaleCalf(Animal):
    name: str = "MaleCalf"
    template_id: int = 298600


# 公牛
@dataclass(init=False)
class Bull(Animal):
    name: str = "Bull"
    template_id: int = 298611


# 奶牛
@dataclass(init=False)
class DairyCow(Animal):
    name: str = "Dairy Cow"
    template_id: int = 298607


supported_animals = [Chicken, Chick, ChickenEgg, BabyCalf, Calf, FeMaleCalf, MaleCalf, DairyCow]

farming_table.update({cls.template_id: cls for cls in supported_animals})


def init_animal_config(rows: List[dict]):
    for item in rows:
        animal_class: Animal = farming_table.get(item["template_id"], None)
        if animal_class:
            animal_class.name = item["name"]
            animal_class.energy_consumed = item["energy_consumed"]
            animal_class.charge_time = timedelta(seconds=item["charge_time"])
            animal_class.required_claims = item["required_claims"]
            animal_class.daily_claim_limit = item["daily_claim_limit"]
            animal_class.consumed_card = item["consumed_card"]
            animal_class.required_building = item["required_building"]


# 动物-从http返回的json数据构造对象
def create_animal(item: dict, breeding=False) -> Animal:
    animal_class = farming_table.get(item["template_id"], None)
    if not animal_class:
        return None
    animal = animal_class()
    animal.day_claims_at = [datetime.fromtimestamp(item) for item in item["day_claims_at"]]
    animal.name = item["name"]
    animal.template_id = item["template_id"]
    animal.times_claimed = item.get("times_claimed", None)
    animal.last_claimed = datetime.fromtimestamp(item["last_claimed"])
    animal.next_availability = datetime.fromtimestamp(item["next_availability"])
    if not breeding:
        animal.asset_id = item["asset_id"]
    else:
        animal.required_claims = 9  # 繁殖目前就只有奶牛，先写死
        animal.daily_claim_limit = 3  # 繁殖目前就只有奶牛，先写死
        animal.consumed_card = 318607  # 繁殖目前就只有奶牛，先写死
        animal.bearer_id = item["bearer_id"]
        animal.partner_id = item["partner_id"]

    return animal


# 动物-从http返回的json数据构造对象
def create_breeding(item: dict) -> Animal:
    animal_class = farming_table.get(item["template_id"], None)
    if not animal_class:
        return None
    animal = animal_class()
    animal.day_claims_at = [datetime.fromtimestamp(item) for item in item["day_claims_at"]]
    animal.asset_id = item["asset_id"]
    animal.name = item["name"]
    animal.template_id = item["template_id"]
    animal.times_claimed = item.get("times_claimed", None)
    animal.last_claimed = datetime.fromtimestamp(item["last_claimed"])
    animal.next_availability = datetime.fromtimestamp(item["next_availability"])
    return animal


####################################################### Animal #######################################################

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


# 大麦种子
@dataclass(init=False)
class BarleySeed(Crop):
    name: str = "Barley Seed"
    template_id: int = 298595
    golds_cost: int = 50


# 玉米种子
@dataclass(init=False)
class CornSeed(Crop):
    name: str = "Corn Seed"
    template_id: int = 298596
    golds_cost: int = 75


supported_crops = [BarleySeed, CornSeed]

farming_table.update({cls.template_id: cls for cls in supported_crops})


def init_crop_config(rows: List[dict]):
    for item in rows:
        crop_class: Crop = farming_table.get(item["template_id"], None)
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

    def __init__(self, template_id, name, type, saved_claims):
        self.name = name
        self.template_id = template_id
        self.type = type
        self.saved_claims = saved_claims

    def show(self, more=True) -> str:
        if more:
            return f"[{self.name}] [类型:{self.type}] [asset_id:{self.asset_id}] [可操作时间:{utils.show_time(self.next_availability)}]"
        else:
            return f"[{self.name}] [类型:{self.type}]"


mbs_table: Dict[int, MBS] = {}


def init_mbs_config(rows: List[dict]):
    for item in rows:
        mbs = MBS(item["template_id"], item["name"], item["type"], item["saved_claims"])
        mbs_table[item["template_id"]] = mbs


# 从json构造mbs对象
def create_mbs(item: dict) -> MBS:
    mbs_class = mbs_table.get(item["template_id"], None)
    if not mbs_class:
        return None
    mbs = MBS(mbs_class.template_id, mbs_class.name, mbs_class.type, mbs_class.saved_claims)
    mbs.asset_id = item["asset_id"]
    mbs.next_availability = datetime.fromtimestamp(item["next_availability"])
    return mbs


####################################################### MBS #######################################################


# 建筑物
@dataclass(init=False)
class Building(Farming):
    # 能量消耗 牛棚300，鸡舍250，田200
    energy_consumed: int = 300
    times_claimed: int = None
    last_claimed: datetime = None
    is_ready: int = None
    slots_used: int = None
    num_slots: int = None


# NFT资产，可以是小麦，小麦种子，牛奶等
@dataclass(init=False)
class Asset:
    asset_id: str
    name: str
    is_transferable: bool
    is_burnable: bool
    schema_name: str
    template_id: str
