# 清华大学每日健康打卡 systemd 版

环境准备：

- 一个 24 小时开机的 Linux 操作系统（需要使用 systemd，如 2015 年以后的 Ubuntu / Debian / CentOS / Fedora 等）
- Python 3，安装有 requests（可以直接安装系统软件源提供的 `python3-requests` 包）

用法：

- 将 `ustc-checkin.py` 复制到 `/root` 目录下
- 将 `ustc-checkin.service` 和 `ustc-checkin.timer` 复制到 `/etc/systemd/system` 目录下，并执行 `systemctl daemon-reload` 和 `systemctl enable ustc-checkin.timer`
- 在 `/root` 目录下创建 `ustc-checkin.txt` 文件，填入以下内容：

    ```ini
    USERNAME=你的CAS登录学号
    PASSWORD=你的CAS登录密码
    PROVINCE=省份代号
    CITY=城市代号
    ```

    其中省份代号和城市代号可以在 [这里](http://www.tcmap.com.cn/list/daima_list.html) 查到。

本套件默认在每天 10:00 至 20:00 之间随机选择一个时间打卡一次，请确保你的系统时钟和时区设置是正确的，或者自行编辑 `ustc-checkin.timer` 文件设置打卡时间。

## 许可

> MIT License
> 
> Copyright (c) 2020 iBug
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.
