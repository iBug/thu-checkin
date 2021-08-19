# 清华大学每日健康打卡 systemd 版

环境要求：

- 一个 24 小时开机的 Linux 操作系统（需要使用 systemd，如 Ubuntu 18.04, Debian Stretch, CentOS 7, Fedora 等，树莓派也行）
- Tesseract
  - Ubuntu 和 Debian 可以直接使用 `apt install tesseract-ocr` 安装，其他发行版请自行解决安装问题
- Python 3，并且安装了一些库：
  - requests（可以直接安装系统软件源提供的 `python3-requests` 包，也可以从 PyPI 安装，没有区别）
  - pillow（`apt install python3-pil` 或 `pip3 install pillow`）
  - pytesseract

用法：

- 将 `thu-checkin.py` 复制到 `/root` 目录下
- 将 `thu-checkin.service` 和 `thu-checkin.timer` 复制到 `/etc/systemd/system` 目录下，并执行 `systemctl daemon-reload` 和 `systemctl enable --now thu-checkin.timer`
- 在 `/root` 目录下创建 [`thu-checkin.txt` 文件](thu-checkin.example.txt)，填入以下内容：

    ```ini
    USERNAME=清华大学用户电子身份服务系统（即 CAS）学号
    PASSWORD=清华大学用户电子身份服务系统（即 CAS）密码
    PROVINCE=省份代号
    CITY=城市代号
    COUNTRY=区县代号
    IS_INSCHOOL=在校状态
    ```

    其中省份、城市和区县代号可以在 [这里](http://www.tcmap.com.cn/list/daima_list.html) 查到。

    在校状态 `IS_INSCHOOL` 的取值为：

    | 值 | 含义     |
    | -- | -------- |
    | 0  | 校外     |
    | 2  | 东区     |
    | 3  | 南区     |
    | 4  | 中区     |
    | 5  | 北区     |
    | 6  | 西区     |
    | 7  | 先研院   |
    | 8  | 国金院   |
    | 9  | 其他校区 |

    默认为 2，即东区。该项目仅当省份城市为安徽合肥（340000 + 340100）时会填报。

本套件默认在北京时间每天 8:00 至 11:00 之间随机选择一个时间打卡一次，请确保你的系统时钟和时区设置是正确的，或者自行编辑 `thu-checkin.timer` 文件设置打卡时间。

你可以使用 `systemctl status thu-checkin.timer` 查看打卡记录和下次打卡时间。

如果你有其他需求，例如打卡结果自动通知等，请自行修改 Python 程序实现。提示：仓库里的 Python 文件末尾已经有判断打卡成功的代码了。

## Docker 方式

请参考 [Dockerfile](Dockerfile) 和 [`run.sh`](run.sh) 自行配置。

## 许可

本项目以 MIT 协议开源，详情请见 [LICENSE](LICENSE) 文件。
