# 清华大学每日健康打卡 systemd 版

推荐点击右上角的 Star 和 Watch 关注本仓库，以及时获知最新更新。

## 环境要求

- 一个 24 小时开机的 Linux 操作系统（需要使用 systemd，如 Ubuntu 18.04, Debian Stretch, CentOS 7, Fedora 等，树莓派也行）
- Tesseract
  - Ubuntu 和 Debian 可以直接使用 `apt install tesseract-ocr` 安装，其他发行版请自行解决安装问题
- Python 3，并且安装了一些库：
  - requests（可以直接安装系统软件源提供的 `python3-requests` 包，也可以从 PyPI 安装，没有区别）
  - pillow（`apt install python3-pil` 或 `pip3 install pillow`）
  - pytesseract

## 使用方法

- 将 `thu-checkin.py` 复制到 `/root` 目录下
- 将 `thu-checkin.service` 和 `thu-checkin.timer` 复制到 `/etc/systemd/system` 目录下，并执行 `systemctl daemon-reload` 和 `systemctl enable --now thu-checkin.timer`
- 在 `/root` 目录下创建 [`thu-checkin.txt` 文件](thu-checkin.example.txt)，填入以下内容：

    ```ini
    [thu-checkin]
    USERNAME=清华大学用户电子身份服务系统学号
    PASSWORD=清华大学用户电子身份服务系统密码
    REASON=进出校原因
    RETURN_COLLEGE=进出校区
    REASON_TEXT=进出校原因
    COMMENT_TEXT=进出校原因备注
    DORM_BUILDING=宿舍楼
    DORM=宿舍

    # 大数据行程🐎
    IMAGE_1=/path/to/1.jpg
    # 北京健康宝
    IMAGE_2=/path/to/2.jpg
    # 核酸报告
    IMAGE_3=/path/to/3.jpg
    ```

    进出校原因 `REASON` 的取值为：

    | 值 | 含义                         |
    | -- | ---------------------------- |
    | 1  | 离校前往北京市外或暂不返校   |
    | 2  | 前往北京市内校外             |
    | 3  | 前往东西南北中校区           |
    | 4  | 前往高新校区、先研院、国金院 |

    请根据实际情况选择一个合适的取值，一般来说根据你的现居地选择 3 或者 4 即可。

    进出校区 `RETURN_COLLEGE` 为一个或多个校区名称，用空格分隔。可以将所有校区都写上（见 example 文件）。

    宿舍楼 `DORM_BUILDING` 和宿舍 `DORM` 直接填写文字。

    上传图片 `IMAGE_1`、`IMAGE_2`、`IMAGE_3` 填写文件路径。若未填写或者指定的路径不存在，则该张图片会被跳过。每张图片的含义如下：

    | 名称      | 含义             |
    | --------- | ---------------- |
    | `IMAGE_1` | 通信大数据行程码 |
    | `IMAGE_2` | 北京健康宝       |
    | `IMAGE_3` | 核酸检测报告     |

本套件默认在系统本地时间每天 8:00 至 11:00 之间随机选择一个时间打卡一次，请确保你的系统时钟和时区设置是正确的，或者自行编辑 `thu-checkin.timer` 文件设置打卡时间。

你可以使用 `systemctl status thu-checkin.timer` 查看打卡记录和下次打卡时间。

如果你有其他需求，例如打卡结果自动通知等，请自行修改 Python 程序实现。提示：仓库里的 Python 文件末尾已经有判断打卡成功的代码了。

### Docker 方式

在仓库目录中构建 Docker 镜像：

```shell
docker build -t checkin:latest .
```

使用 `run.sh` 运行：

```shell
./run.sh
```

详细信息请参考 [Dockerfile](Dockerfile) 和 [`run.sh`](run.sh)。

## 许可

本项目以 MIT 协议开源，详情请见 [LICENSE](LICENSE) 文件。
