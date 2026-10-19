# 🌐 Domain Resolution & IP Lookup

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)](https://www.docker.com/)

A lightweight domain and IP lookup tool with a Python backend, concurrency control, and caching. Designed to be clean, ad-free, and ready to use.

## Features

- **Dual stack:** IPv4 and IPv6 detection and geolocation.
- **Global DNS queries:** concurrent resolution through Google, Cloudflare, Aliyun, and Tencent.
- **WHOIS details:** structured field extraction, with a terminal-style raw response fallback for less common new gTLDs.
- **In-memory caching:** `TimedCache` keeps results for 12 hours to reduce latency and upstream quota usage.
- **Interface:** English and Chinese, responsive layout, and automatic dark mode.

## Technology

- Frontend: HTML5, vanilla JavaScript, Tailwind CSS via CDN.
- Backend: Python, FastAPI, Uvicorn.
- Libraries: `requests`, `dnspython`, `python-whois`, and `tldextract`.
- Data sources: [ip-api.com](https://ip-api.com/) with free-tier rate-limit protection, and authoritative WHOIS servers.

## Deployment

### Server management panel

1. Upload the repository to a directory such as `/opt/ip-query`.
2. In the panel's container image tools, build `ip-query:v1` from that directory.
3. Create a container from the image and map port `8000:8000`.

Configure a reverse proxy to add a domain and HTTPS. The same workflow can be used in 1Panel or other Docker-capable management panels.

### Docker Compose

Install Git, Docker, and Docker Compose, then run:

```bash
git clone https://github.com/JohnMuyuan/iplookup.git
cd iplookup
docker-compose up -d
```

## Customize the interface

Edit `index.html` to change interface text, including the title and footer.
