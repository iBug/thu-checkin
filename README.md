# 清华大学每日健康打卡 systemd 版

## 使用方法一（自己部署，推荐）

环境要求：

- 一个 24 小时开机的 Linux 操作系统（需要使用 systemd，如 Ubuntu 16.04, Debian Jessie, CentOS 7, Fedora 等，树莓派也行）
- Python 3，安装有 requests（可以直接安装系统软件源提供的 `python3-requests` 包，也可以从 PyPI 安装，没有区别）

用法：

- 将 `ustc-checkin.py` 复制到 `/root` 目录下
- 将 `ustc-checkin.service` 和 `ustc-checkin.timer` 复制到 `/etc/systemd/system` 目录下，并执行 `systemctl daemon-reload` 和 `systemctl enable --now ustc-checkin.timer`
- 在 `/root` 目录下创建 `ustc-checkin.txt` 文件，填入以下内容：

    ```ini
    USERNAME=你的CAS登录学号
    PASSWORD=你的CAS登录密码
    PROVINCE=省份代号
    CITY=城市代号
    ```

    其中省份代号和城市代号可以在 [这里](http://www.tcmap.com.cn/list/daima_list.html) 查到。

本套件默认在每天 10:00 至 18:00 之间随机选择一个时间打卡一次，请确保你的系统时钟和时区设置是正确的，或者自行编辑 `ustc-checkin.timer` 文件设置打卡时间。

你也可以使用 `systemctl status ustc-checkin.timer` 查看打卡记录和下次打卡时间。

## 使用方法二（GitHub Actions，不推荐）

- [Fork](https://github.com/iBug/ustc-checkin/fork) 本仓库
- 转到你 fork 的仓库，进入 Settings → Secrets，按上面说明添加四个 Secret，如图：

    ![image](https://user-images.githubusercontent.com/7273074/82295949-0fcde880-99e3-11ea-956b-fddbd003c3bc.png)

本方法默认在每天 10:00 打卡一次，不支持随机时间，也可以自行编辑 `checkin.yml` 设置打卡时间。

## 许可

本项目以 MIT 协议开源，详情请见 [LICENSE](LICENSE) 文件。
