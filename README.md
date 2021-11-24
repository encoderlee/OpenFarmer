## OpenFarmer
### 一个免费、开源的农民世界 FarmersWorld 挂机脚本
![image](https://raw.githubusercontent.com/encoderlee/OpenFarmer/main/doc/demo1.png)
### 初衷

农民世界 https://farmersworld.io 的火热相信大家已经有目共睹

网上各种辅助脚本也是满天飞，可是2021年11月7日的大面积盗号事件让广大farmer伤心和愤怒

于是我决定免费开源自己写的一个简陋的挂机脚本，没有华丽的界面，只有简单的配置文件和命令行，虽然不好看，但是绝对可用

代码完全公开，不含任何二进制可执行文件，不含任何后门的病毒，完全经得住检验

同时，欢迎大家提 BUG 和 Push 代码，不断的完善它

本项目使用 python3 + selenium 开发

跨平台运行，支持 Windows、Linux、MacOS

原理思路见：https://blog.csdn.net/CharlesSimonyi/article/details/121413962

也欢迎关注我的CSDN博客

欢迎加入 Telegram 群组：https://t.me/OpenFarmer

### 功能
由于此项目本来是个人自用的，而我自己只种种田，所以并没有完成所有的功能，目前仅支持一下操作，但后面会不断的完善

1. 支持一台电脑上多开
2. 支持设置HTTP代理
3. 支持Mining下的所有工具（斧头、石斧、锯子、钓鱼竿、渔网、渔船、挖掘机等）的自动采集
4. 支持Plant下的所有农作物（大麦、玉米）的自动采集
5. 支持Chicken下（鸡）的自动喂养，（鸡蛋和小鸡）暂不支持
6. 养牛暂不支持
7. 支持会员卡的自动点击
8. 工具耐久不足自动修理（请准备好足够修理的金币）
9. 能量不足自动补充（请准备好足够的肉）
10. 支持自动建造（新号第一次建造 COOP 和 FARM PLOT需要点8次的操作）
11. 其它功能正在补充中。。。

### 用法
1. git clone 源码到本地，或 Download ZIP 下载源码到本地
2. 下载安装python3 (版本须大于等于python3.7)
   
   请到python官网下载最新版本：
   https://www.python.org/downloads/
   
   【注意】安装时请记得勾选【Add Python 3.10 to PATH】
3. 双击运行 【install_depends.py】 来安装依赖包，一台电脑只需要安装一次即可
4. 安装Chrome浏览器，并升级到最新版
5. 下载ChromeDriver，版本确保和Chrome版本一致
https://chromedriver.chromium.org/downloads

    比如我的Chrome版本是 96.0.4664.45

    那么我就下载 ChromeDriver 96.0.4664.45

    其实小版本不一致也没关系，大版本号96一致就行

6. 将下载的 ChromeDriver 压缩包中的 chromedriver.exe 文件，解压到本项目的源码目录中（和 main.py 在一个目录中）
7. 修改配置文件【user.yaml】
   
   wax_account: (wax账号，也就是wax钱包地址,以.wam结尾)
   
   proxy: (可设置http代理，格式为127.0.0.1:10809，不需要代理的话设置为null)

   下面的（build、mining、chicken、plant、cow、mbs)分别对应建造、采集资源、养鸡、种地、养牛、会员点击，需要程序自动化的操作，设置为true，不需要程序自动化的操作，设置为false，比如你只种地的话，plant: true 即可，其它全部为false，这样减少不必要的网络操作，提高运行效率

   recover_energy: 500 (能量不够时恢复到多少能量，默认500，请准备足够的肉，程序不会自动去买肉)
8. 修改完配置文件后，双击 【main.py】 运行脚本，程序如果异常退出，可以到 logs 文件夹下查看日志
9. 脚本启动后，会弹出一个Chrome窗口并自动打开 FarmersWorld 官网，第一次启动请手工登录游戏，登录成功后，脚本会开始自动化操作
10. 如果需要手工操作，请勿在脚本打开的Chrome窗口中操作，脚本打开的Chrome窗口，最小化即可，尽量不要动它，需要手工操作的时候，请另开Chrome浏览器登录游戏，该游戏本身就可同时在多个浏览器中登录，不会把脚本Chrome中的游戏T下线
11. 脚本多开，请把整个源码目录复制一份，在另一个目录中修改配置文件【user.yaml】为另一个账号，双击运行 【main.py】 启动第二个脚本，以此类推，多开互不干扰

### 打赏
欢迎打赏，支持我继续不断完善这个项目

0xeaC7d998684F50b7A492EA68F27633a117Be201d

支持USDT、ETH、BUSD、BNB等，以及 Ethereum、BSC等网络上的任何ERC20代币，感谢
