# 🌐 轻量级域名解析 & IP查询 (Deep IP & WHOIS Intelligence)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)](https://www.docker.com/)

一个轻量、优雅且功能强大的域名与 IP 综合查询工具。配合支持并发控制与缓存保护的高性能 Python 后端，为您提供秒级的查询体验。

> 💡 **项目初衷：** 打造一个干净、无广告、开箱即用的域名&IP工具。

## ✨ 核心特性

*   **双栈支持：** 原生支持 IPv4 与 IPv6 地址的精准识别与归属地定位。
*   **全球 DNS 矩阵：** 多节点 DNS 并发查询（Google / Cloudflare / Aliyun / Tencent）。
*   **深度 WHOIS 溯源：** 内置结构化信息提取引擎；针对罕见新顶级域（New gTLDs），自动降级为极客 Terminal 模式展示原生报文。
*   **企业级内存缓存：** 后端内置 `TimedCache` 机制，自动缓存 12 小时查询结果。实现“越查越快”的秒开体验，节省上游接口的免费调用配额。
*   **极致 UI 体验：** 极简设计语言，支持 i18n 一键中英文切换，完美适配自适应暗黑模式 (Dark Mode)。

## 📸 界面预览

![image-CkrF.png](https://op.style/upload/WebSer/image-CkrF.png)
![image-kcZz.png](https://op.style/upload/WebSer/image-kcZz.png)
![image-yJLd.png](https://op.style/upload/WebSer/image-yJLd.png)
![image-wPhJ.png](https://op.style/upload/WebSer/image-wPhJ.png)
![image-Phbr.png](https://op.style/upload/WebSer/image-Phbr.png)
![image-lrOb.png](https://op.style/upload/WebSer/image-lrOb.png)

## 🛠️ 技术栈

*   **前端:** HTML5, 原生 JavaScript, TailwindCSS (CDN 引入)
*   **后端:** Python, FastAPI, Uvicorn
*   **核心库:** `requests` (API 请求), `dnspython` (全球解析), `python-whois` / `tldextract` (根域名与溯源)
*   **数据源:** [ip-api.com](https://ip-api.com/) (免费版限流保护已生效), 各大根服务器

---

## 🚀 部署指南 (Deployment)

本项目支持 Docker 容器化一键本地构建，无需手动配置 Python 环境，极其干净轻量！

### 方法一：使用 1Panel / 宝塔面板部署

如果你使用 1Panel 服务器管理面板，只需三步即可上线：
1. **下载代码：** 在 1Panel 左侧菜单进入 **主机 -> 文件**，新建一个文件夹（如 `/opt/ip-query`），并将本仓库的所有文件上传到该目录下。
2. **构建镜像：** 进入 **容器 -> 镜像**，点击“构建镜像”。名称填 `ip-query:v1`，目录选择你刚才上传文件的文件夹，点击确认构建。
3. **创建容器：** 进入 **容器 -> 容器**，点击“创建容器”。选择刚建好的 `ip-query:v1` 镜像，端口映射填写 `8000:8000`，点击确认即可跑通！
*(最后在“网站”功能中添加反向代理，即可绑定域名并开启 HTTPS)*

### 方法二：使用命令行 Docker Compose 部署

如果你喜欢命令行，确保你的服务器已安装 `git`、`docker` 和 `docker-compose`：

```bash
# 1. 将项目克隆到你的服务器
git clone https://github.com/JohnMuyuan/iplookup.git
cd iplookup

# 2. 一键自动构建镜像并后台启动服务
docker-compose up -d
