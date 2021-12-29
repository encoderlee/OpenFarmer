## OpenFarmer

>该脚本基于https://github.com/encoderlee/OpenFarmer 开发，在他的功能基础上增加了一些功能，感谢这位大佬无私奉献。

### 一个免费、开源的农民世界 FarmersWorld 挂机脚本
![image](https://raw.githubusercontent.com/encoderlee/OpenFarmer/main/doc/demo1.png)
### 初衷

农民世界 https://farmersworld.io 的火热相信大家已经有目共睹

网上各种辅助脚本也是满天飞，可是2021年11月7日某脚本商实施的大面积盗号事件让广大farmer伤心和愤怒

于是我决定免费开源自己写的一个简陋的挂机脚本，没有华丽的界面，只有简单的配置文件和命令行，虽然不好看，但是绝对安心可用

代码完全公开，不含任何二进制可执行文件，不含任何后门病毒，完全经得住检验

同时，欢迎大家提 BUG 和 Push 代码，不断的完善它

本项目使用 python3 + selenium 开发

跨平台运行，支持 Windows、Linux、MacOS

原理思路见：https://blog.csdn.net/CharlesSimonyi/article/details/121413962

也欢迎关注我的CSDN博客

欢迎加入 Telegram 群组反馈问题：https://t.me/OpenFarmer

### 功能

1. 支持一台电脑上多开
2. 支持设置HTTP代理
3. 支持Mining下的所有工具（斧头、石斧、锯子、钓鱼竿、渔网、渔船、挖掘机等）的自动采集
4. 支持Plant下的所有农作物（大麦、玉米）的自动浇水，自动种地
5. 支持鸡蛋->小鸡->鸡的自动喂养
6. 支持小牛犊->小牛->奶牛的喂养
7. 支持会员卡的自动点击
8. 工具耐久不足自动修理（请准备好足够修理的金币）
9. 能量不足自动补充（请准备好足够的肉）
10. 支持自动建造（新号第一次建造 COOP 和 FARM PLOT需要点8次的操作）
11. 支持鸡蛋、牛奶、大麦、玉米自动售卖
12. 支持食物、金子不足自动充值
13. 支持5%费率的时候自动提现

### 用法
1. git clone 源码到本地，或 Download ZIP 下载源码到本地
2. 下载安装python3 (版本须大于等于python3.7)
   
   请到python官网下载最新版本：
   https://www.python.org/downloads/
   
   【注意】安装时请记得勾选【Add Python 3.10 to PATH】
3. 双击运行 【install_depends.py】 来安装依赖包，一台电脑只需要安装一次即可
   【注意】安装依赖包前请关闭翻墙代理，关闭科学上网，不然无法从豆瓣pypi镜像站下载依赖包
4. 安装Chrome浏览器，并升级到最新版
5. 下载ChromeDriver，版本确保和Chrome版本一致
https://chromedriver.chromium.org/downloads

    比如我的Chrome版本是 96.0.4664.45

    那么我就下载 ChromeDriver 96.0.4664.45

    其实小版本不一致也没关系，大版本号96一致就行
   
   windows系统的话下载【chromedriver_win32.zip】
6. 将下载的 ChromeDriver 压缩包中的 chromedriver.exe 文件，解压到本项目的源码目录中（和 main.py 在一个目录中）
7. 修改配置文件【user.yaml】 
   1. 复制user.yaml.example 到 user.yaml
   2. 按照你的实际情况设置各个参数
   3. wax_account: (wax账号，也就是wax钱包地址,以.wam结尾)
   4. proxy: (可设置http代理，格式为127.0.0.1:10809，不需要代理的话设置为null)
   5. 下面的（build、mining、animal、plant、mbs)分别对应建造、采集资源、养鸡、种地、养牛、会员点击，需要程序自动化的操作，设置为true，不需要程序自动化的操作，设置为false，比如你只种地的话，plant: true 即可，其它全部为false，这样减少不必要的网络操作，提高运行效率 
   6. recover_energy: 500 (能量不够时恢复到多少能量，默认500，请准备足够的肉，程序不会自动去买肉)
   7. 建造、采集资源、养动物、种地、会员点击，需要程序自动化的操作，设置为true
   8. 其他参数按照你的实际情况设置
   
8. 修改完配置文件后，双击 【main.py】 运行脚本，程序如果异常退出，可以到 logs 文件夹下查看日志
9. 脚本启动后，会弹出一个Chrome窗口并自动打开 FarmersWorld 官网，第一次启动请手工登录游戏，登录成功后，脚本会开始自动化操作
10. 如果需要手工操作，请勿在脚本打开的Chrome窗口中操作，脚本打开的Chrome窗口，最小化即可，尽量不要动它，需要手工操作的时候，请另开Chrome浏览器登录游戏，该游戏本身就可同时在多个浏览器中登录，不会把脚本Chrome中的游戏T下线
11. 注意，一个账号第一次运行脚本，脚本第一次自动收割农作物的时候，Chrome浏览器中可能会弹出WAX钱包授权窗口，并停在那里不动了，这个时候需要勾选自动确认交易，并同意交易，这样脚本以后就能自动处理了，其实和人工操作是一样的，第一次收割的时候，也要点自动同意交易，否则每次都要弹出授权窗口来，脚本只负责收割农作物，不处理授权的事情，是否自动授权取决于用户账号设置
12. 脚本多开，请把整个源码目录复制一份，在另一个目录中修改配置文件【user.yaml】为另一个账号，双击运行 【main.py】 启动第二个脚本，以此类推，多开互不干扰
13. 正确关闭程序，请点击脚本控制台窗口右上角的X，稍等几秒钟便会关闭，或者点击脚本控制台窗口后，按Ctrl+C，尽量不要直接关闭脚本控制的Chrome窗口，否则webdriver容易产生一些僵尸进程

### 常见问题
1.程序日志显示，已经成功喂鸡，成功浇水，成功采集了，为什么Chrome中的游戏界面上还是显示没有喂鸡，没有浇水，没有采集？

这是因为程序是通过直接调用智能合约的方式进行的操作，Chrome中游戏界面并不会自动更新，实际上只要日志显示操作成功，就已经操作成功了，Chrome中的游戏界面不更新，无需理会，你可以重新开一个Chrome窗口，重新登录游戏查看，到底操作成功了没有

2.无法使用google账号登录，提示此浏览器或应用可能不安全？

![image](https://raw.githubusercontent.com/encoderlee/OpenFarmer/main/doc/question1.png)

这是因为Chrome本身就是google家的，google判断到该Chrome浏览器正受程序控制，便判定为不安全，不允许登录。解决办法就是在WAX云钱包登录界面，点【Forgot Password】（忘记密码），输入google邮箱账号，根据提示重置密码（可以重置为和原来一样的密码），重置成功后，便可在WAX云钱包登录界面，直接输入google邮箱账号和重置后的密码进行登录，而不需要点google图标，不需要通过google账号登录。


### 打赏

欢迎打赏，支持我继续不断完善这个项目

TRC20地址: TXmvTZ3ndHpvJU7SYmuLdLBufWdxA34Qix

WAX地址：4lrzu.wam（支持WAX、FWW、FWF、FWG）

### 感谢!
