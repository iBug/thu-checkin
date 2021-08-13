# 清华大学每日健康打卡 systemd 版

环境要求：

- 一个 24 小时开机的 Linux 操作系统（需要使用 systemd，如 Ubuntu 16.04, Debian Jessie, CentOS 7, Fedora 等，树莓派也行）
- Python 3，安装有 requests（可以直接安装系统软件源提供的 `python3-requests` 包，也可以从 PyPI 安装，没有区别）

用法：

- 将 `ustc-checkin.py` 复制到 `/root` 目录下
- 将 `ustc-checkin.service` 和 `ustc-checkin.timer` 复制到 `/etc/systemd/system` 目录下，并执行 `systemctl daemon-reload` 和 `systemctl enable --now ustc-checkin.timer`
- 在 `/root` 目录下创建 [`ustc-checkin.txt` 文件](ustc-checkin.example.txt)，填入以下内容：

    ```ini
    USERNAME=你的CAS登录学号
    PASSWORD=你的CAS登录密码
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

本套件默认在每天 10:00 至 18:00 之间随机选择一个时间打卡一次，请确保你的系统时钟和时区设置是正确的，或者自行编辑 `ustc-checkin.timer` 文件设置打卡时间。

你可以使用 `systemctl status ustc-checkin.timer` 查看打卡记录和下次打卡时间。

## 许可

本项目以 MIT 协议开源，详情请见 [LICENSE](LICENSE) 文件。
