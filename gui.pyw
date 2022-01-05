from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt6 import QtGui
from dialog import Ui_Dialog
import logging
from farmer import Farmer
import logger
from logger import log
import yaml
import sys
import utils
from settings import load_user_param, user_param
import os

version = "1.1"


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class QTextEditLogHandler(QObject, logging.Handler):
    signal_log = pyqtSignal(str)

    def emit(self, record):
        msg = self.format(record)
        self.signal_log.emit(msg)


class Worker(QThread):
    def __init__(self, farmer: Farmer):
        super().__init__()
        self.farmer = farmer

    def run(self):
        logger.init_loger(user_param.wax_account)
        log.info("wax_account; {0}".format(user_param.wax_account))
        utils.clear_orphan_webdriver()
        self.farmer.wax_account = user_param.wax_account
        if user_param.use_proxy:
            self.farmer.proxy = user_param.proxy
            log.info("use proxy: {0}".format(user_param.proxy))
        self.farmer.init()
        self.farmer.start()
        log.info("开始自动化，请勿刷新浏览器，如需手工操作建议新开一个浏览器操作")
        return self.farmer.run_forever()


class MyDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_yml = "user.yml"
        self.farmer = Farmer()
        self.setupUi(self)
        self.setWindowTitle("农民世界助手{0}".format(version))
        self.setWindowIcon(QtGui.QIcon(resource_path("favicon.ico")))
        self.setWindowFlags(Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        self.setFixedSize(self.size())
        self.button_start.clicked.connect(self.start)
        handler = QTextEditLogHandler()
        handler.signal_log.connect(self.show_log)
        #logging_format = logging.Formatter("[%(asctime)s][%(levelname)s][%(process)d]: %(message)s")
        logging_format = logging.Formatter("[%(asctime)s][%(tag)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(logging_format)
        logging.getLogger().addHandler(handler)
        self.load_yaml()
        self.worker = Worker(self.farmer)

    def load_yaml(self):
        if len(sys.argv) == 2:
            self.user_yml = sys.argv[1]
        with open(self.user_yml, "r", encoding="utf8") as file:
            user: dict = yaml.load(file, Loader=yaml.FullLoader)
            file.close()
        load_user_param(user)
        self.update_ui(False)

    def update_ui(self, ui_to_user_param: bool):
        if ui_to_user_param:
            user_param.wax_account = self.edit_account.text()
            user_param.use_proxy = self.checkbox_proxy.isChecked()
            user_param.proxy = self.edit_proxy.text()
            user_param.build = self.checkbox_build.isChecked()
            user_param.mining = self.checkbox_mining.isChecked()
            user_param.chicken = self.checkbox_chicken.isChecked()
            user_param.plant = self.checkbox_plant.isChecked()
            user_param.cow = self.checkbox_cow.isChecked()
            user_param.mbs = self.checkbox_mbs.isChecked()
            user_param.recover_energy = self.spinbox_energy.value()
            user_param.min_energy = self.spinbox_min_energy.value()
            user_param.min_durability = self.spinbox_min_durability.value()
            # 自动提现
            user_param.withdraw = self.checkbox_withdraw.isChecked()
            user_param.need_fww = int(self.need_fww.text())
            user_param.need_fwf = int(self.need_fwf.text())
            user_param.need_fwg = int(self.need_fwg.text())
            user_param.withdraw_min = int(self.withdraw_min.text())
            # 自动充值
            user_param.auto_deposit = self.checkbox_auto_deposit.isChecked()
            user_param.fww_min = int(self.fww_min.text())
            user_param.fwf_min = int(self.fwf_min.text())
            user_param.fwg_min = int(self.fwg_min.text())
            user_param.deposit_fww = int(self.deposit_fww.text())
            user_param.deposit_fwf = int(self.deposit_fwf.text())
            user_param.deposit_fwg = int(self.deposit_fwg.text())
            # 卖玉米
            user_param.sell_corn = self.checkbox_sell_corn.isChecked()
            user_param.remaining_corn_num = int(self.remaining_corn_num.text())
            # 卖大麦
            user_param.sell_barley = self.checkbox_sell_barley.isChecked()
            user_param.remaining_barley_num = int(self.remaining_barley_num.text())
            # 卖牛奶
            user_param.sell_milk = self.checkbox_sell_milk.isChecked()
            user_param.remaining_milk_num = int(self.remaining_milk_num.text())
            # 卖鸡蛋
            user_param.sell_egg = self.checkbox_sell_egg.isChecked()
            user_param.remaining_egg_num = int(self.remaining_egg_num.text())
            # 自动播种
            user_param.auto_plant = self.checkbox_auto_plant.isChecked()
            user_param.barleyseed_num = int(self.barleyseed_num.text())
            user_param.cornseed_num = int(self.cornseed_num.text())
            # 自动购买
            user_param.buy_food = self.checkbox_buy_food.isChecked()
            user_param.buy_barley_seed = self.checkbox_buy_barley_seed.isChecked()
            user_param.buy_corn_seed = self.checkbox_buy_corn_seed.isChecked()
            user_param.buy_food_num = int(self.buy_food_num.text())
            # 自动购买
            user_param.breeding = self.checkbox_breeding.isChecked()

        else:
            self.edit_account.setText(user_param.wax_account)
            self.checkbox_proxy.setChecked(user_param.use_proxy)
            self.edit_proxy.setText(user_param.proxy)
            self.checkbox_build.setChecked(user_param.build)
            self.checkbox_mining.setChecked(user_param.mining)
            self.checkbox_chicken.setChecked(user_param.chicken)
            self.checkbox_plant.setChecked(user_param.plant)
            self.checkbox_cow.setChecked(user_param.cow)
            self.checkbox_mbs.setChecked(user_param.mbs)
            self.spinbox_energy.setValue(user_param.recover_energy)
            self.spinbox_min_energy.setValue(user_param.min_energy)
            self.spinbox_min_durability.setValue(user_param.min_durability)
            # 自动提现
            self.checkbox_withdraw.setChecked(user_param.withdraw)
            self.need_fww.setText(str(user_param.need_fww))
            self.need_fwf.setText(str(user_param.need_fwf))
            self.need_fwg.setText(str(user_param.need_fwg))
            self.withdraw_min.setText(str(user_param.withdraw_min))
            # 自动充值
            self.checkbox_auto_deposit.setChecked(user_param.auto_deposit)
            self.fww_min.setText(str(user_param.fww_min))
            self.fwf_min.setText(str(user_param.fwf_min))
            self.fwg_min.setText(str(user_param.fwg_min))
            self.deposit_fww.setText(str(user_param.deposit_fww))
            self.deposit_fwf.setText(str(user_param.deposit_fwf))
            self.deposit_fwg.setText(str(user_param.deposit_fwg))
            # 卖玉米
            self.checkbox_sell_corn.setChecked(user_param.sell_corn)
            self.remaining_corn_num.setText(str(user_param.remaining_corn_num))
            # 卖大麦
            self.checkbox_sell_barley.setChecked(user_param.sell_barley)
            self.remaining_barley_num.setText(str(user_param.remaining_barley_num))
            # 卖牛奶
            self.checkbox_sell_milk.setChecked(user_param.sell_milk)
            self.remaining_milk_num.setText(str(user_param.remaining_milk_num))
            # 卖鸡蛋
            self.checkbox_sell_egg.setChecked(user_param.sell_egg)
            self.remaining_egg_num.setText(str(user_param.remaining_egg_num))
            # 自动播种
            self.checkbox_auto_plant.setChecked(user_param.auto_plant)
            self.barleyseed_num.setText(str(user_param.barleyseed_num))
            self.cornseed_num.setText(str(user_param.cornseed_num))
            # 自动购买
            self.checkbox_buy_food.setChecked(user_param.buy_food)
            self.checkbox_buy_barley_seed.setChecked(user_param.buy_barley_seed)
            self.checkbox_buy_corn_seed.setChecked(user_param.buy_corn_seed)
            self.buy_food_num.setText(str(user_param.buy_food_num))
            # 繁殖
            self.checkbox_breeding.setChecked(user_param.breeding)

    def setEnabled(self, status: bool):
        self.checkbox_cow.setEnabled(status)
        self.checkbox_build.setEnabled(status)
        self.checkbox_plant.setEnabled(status)
        self.checkbox_mining.setEnabled(status)
        self.checkbox_mbs.setEnabled(status)
        self.checkbox_proxy.setEnabled(status)
        self.checkbox_chicken.setEnabled(status)
        self.edit_proxy.setEnabled(status)
        self.edit_account.setEnabled(status)
        self.spinbox_energy.setEnabled(status)
        self.button_start.setEnabled(status)

        self.spinbox_min_energy.setEnabled(status)
        self.spinbox_min_durability.setEnabled(status)
        # 自动提现
        self.checkbox_withdraw.setEnabled(status)
        self.need_fww.setEnabled(status)
        self.need_fwf.setEnabled(status)
        self.need_fwg.setEnabled(status)
        self.withdraw_min.setEnabled(status)
        # 自动充值
        self.checkbox_auto_deposit.setEnabled(status)
        self.fww_min.setEnabled(status)
        self.fwf_min.setEnabled(status)
        self.fwg_min.setEnabled(status)
        self.deposit_fww.setEnabled(status)
        self.deposit_fwf.setEnabled(status)
        self.deposit_fwg.setEnabled(status)
        # 卖玉米
        self.checkbox_sell_corn.setEnabled(status)
        self.remaining_corn_num.setEnabled(status)
        # 卖大麦
        self.checkbox_sell_barley.setEnabled(status)
        self.remaining_barley_num.setEnabled(status)
        # 卖牛奶
        self.checkbox_sell_milk.setEnabled(status)
        self.remaining_milk_num.setEnabled(status)
        # 卖鸡蛋
        self.checkbox_sell_egg.setEnabled(status)
        self.remaining_egg_num.setEnabled(status)
        # 自动播种
        self.checkbox_auto_plant.setEnabled(status)
        self.barleyseed_num.setEnabled(status)
        self.cornseed_num.setEnabled(status)
        # 自动购买
        self.checkbox_buy_food.setEnabled(status)
        self.checkbox_buy_barley_seed.setEnabled(status)
        self.checkbox_buy_corn_seed.setEnabled(status)
        self.buy_food_num.setEnabled(status)
        # 繁殖
        self.checkbox_breeding.setEnabled(status)
        for i in range(1, 24):
            exec('self.label_{}.setEnabled(status)'.format(i))

    def start(self):
        self.setEnabled(False)
        self.setWindowTitle("农民世界助手{0}【{1}】".format(version, self.edit_account.text()))
        self.update_ui(True)
        self.worker.start()

    def show_log(self, line: str):
        self.plain_text_edit.appendPlainText(line)

    def stop(self):
        self.update_ui(True)
        self.setEnabled(True)
        with open(self.user_yml, "w") as file:
            yaml.dump(user_param.to_dict(), file, default_flow_style=False, sort_keys=False)
        self.plain_text_edit.appendPlainText("稍等，程序正在退出...")
        self.repaint()
        self.farmer.close()
        self.plain_text_edit.appendPlainText("程序已退出")

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    ui = MyDialog()
    ui.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
