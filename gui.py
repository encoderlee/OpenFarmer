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
        if user_param.proxy:
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
        self.setWindowFlags(Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        self.setFixedSize(self.size())
        self.button_start.clicked.connect(self.start)
        handler = QTextEditLogHandler()
        handler.signal_log.connect(self.show_log)
        logging_format = logging.Formatter("[%(asctime)s][%(levelname)s][%(process)d]: %(message)s")
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


    def start(self):
        self.checkbox_cow.setEnabled(False)
        self.checkbox_build.setEnabled(False)
        self.checkbox_plant.setEnabled(False)
        self.checkbox_mining.setEnabled(False)
        self.checkbox_mbs.setEnabled(False)
        self.checkbox_proxy.setEnabled(False)
        self.checkbox_chicken.setEnabled(False)
        self.edit_proxy.setEnabled(False)
        self.edit_account.setEnabled(False)
        self.spinbox_energy.setEnabled(False)
        self.button_start.setEnabled(False)
        self.setWindowTitle("农民世界助手【{0}】".format(self.edit_account.text()))
        self.update_ui(True)
        self.worker.start()

    def show_log(self, line: str):
        self.plain_text_edit.appendPlainText(line)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.update_ui(True)
        with open(self.user_yml, "w") as file:
            yaml.dump(user_param.to_dict(), file, default_flow_style=False, sort_keys = False)
        self.plain_text_edit.appendPlainText("稍等，程序正在退出...")
        self.repaint()
        self.farmer.close()
        event.accept()



def main():
    app = QApplication(sys.argv)
    ui = MyDialog()
    ui.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
