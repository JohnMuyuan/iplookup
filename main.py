from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import socket
import requests
import ipaddress
import whois
import tldextract
from datetime import datetime
import dns.resolver
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🛡️ 企业级内存缓存 (防并发/防刷/保护 API 免费额度) ---
class TimedCache:
    def __init__(self, ttl=43200): # 默认缓存 12 小时
        self.cache = {}
        self.ttl = ttl
        
    def get(self, key):
        if key in self.cache:
            val, ts = self.cache[key]
            if time.time() - ts < self.ttl:
                return val
            del self.cache[key] # 过期清除
        return None
        
    def set(self, key, val):
        self.cache[key] = (val, time.time())

# 初始化全局缓存对象
query_cache = TimedCache() 

DNS_SERVERS = {
    "Google (Global)": "8.8.8.8",
    "Cloudflare (Global)": "1.1.1.1",
    "Aliyun (China)": "223.5.5.5",
    "Tencent (China)": "119.29.29.29"
}

def resolve_custom_dns(domain: str):
    results = {}
    for name, ns_ip in DNS_SERVERS.items():
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [ns_ip]
        resolver.timeout = 2
        resolver.lifetime = 2
        try:
            answers = resolver.resolve(domain, 'A')
            results[name] = str(answers[0])
        except Exception:
            try:
                answers = resolver.resolve(domain, 'AAAA')
                results[name] = str(answers[0])
            except Exception:
                results[name] = "Timeout/Error"
    return results

def get_ip_from_target(target: str) -> str:
    target = target.strip()
    try:
        return str(ipaddress.ip_address(target))
    except ValueError:
        pass
    try:
        res = socket.getaddrinfo(target, None, socket.AF_UNSPEC)
        if res: return res[0][4][0]
    except socket.gaierror:
        pass
    raise ValueError("无法解析目标")

def format_date(d):
    if not d: return "Unknown"
    if isinstance(d, list): d = d[0]
    if isinstance(d, datetime): return d.strftime("%Y-%m-%d %H:%M:%S")
    return str(d)

def format_list(lst):
    if not lst: return "Unknown"
    if isinstance(lst, list): return "<br>".join(list(set([str(i) for i in lst])))
    return str(lst)

@app.get("/")
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/query")
def query_domain_or_ip(target: str, lang: str = "zh-CN"):
    target = target.strip().lower()
    
    # 1. 拦截层：命中缓存直接秒回，不消耗任何外部 API
    cache_key = f"{target}_{lang}"
    cached_result = query_cache.get(cache_key)
    if cached_result:
        return cached_result

    is_ip_input = False
    try:
        ipaddress.ip_address(target)
        is_ip_input = True
        ip_address = target
    except ValueError:
        try:
            ip_address = get_ip_from_target(target)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Domain or IP")

    api_lang = "en" if lang == "en" else "zh-CN"

    # 2. 混合架构A：主 IP 使用单点接口 (彻底修复 rDNS 丢失的 Bug)
    try:
        main_ip_url = f"http://ip-api.com/json/{ip_address}?fields=status,message,continent,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query&lang={api_lang}"
        main_ip_data = requests.get(main_ip_url, timeout=10).json()
        if main_ip_data.get("status") != "success":
            raise HTTPException(status_code=500, detail=f"API Error: {main_ip_data.get('message')}")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Timeout")

    ip_data_map = {ip_address: main_ip_data}
    multi_dns_results = {}
    rich_multi_dns = []

    # 3. 混合架构B：多节点使用 Batch 接口 (只查基础地名不查 rDNS)
    if not is_ip_input:
        multi_dns_results = resolve_custom_dns(target)
        dns_ips_to_query = set()
        for ip in multi_dns_results.values():
            try:
                ipaddress.ip_address(ip)
                if ip != ip_address: # 排除主 IP，节省额度
                    dns_ips_to_query.add(ip)
            except ValueError:
                pass
        
        if dns_ips_to_query:
            try:
                batch_url = f"http://ip-api.com/batch?fields=status,country,city,isp,as,query&lang={api_lang}"
                batch_resp = requests.post(batch_url, json=list(dns_ips_to_query), timeout=10).json()
                for res in batch_resp:
                    if res.get("status") == "success":
                        ip_data_map[res["query"]] = res
            except requests.exceptions.RequestException:
                pass # Batch 失败不影响主流程展示
        
        for node_name, ip in multi_dns_results.items():
            if ip in ip_data_map:
                d = ip_data_map[ip]
                rich_multi_dns.append({
                    "node": node_name,
                    "ip": ip,
                    "status": "success",
                    "country": d.get("country", "Unknown"),
                    "city": d.get("city", "Unknown"),
                    "isp": d.get("isp", "Unknown"),
                    "asn": d.get("as", "Unknown")
                })
            else:
                rich_multi_dns.append({"node": node_name, "ip": ip, "status": "error"})
    else:
        for node_name in DNS_SERVERS.keys():
            rich_multi_dns.append({
                "node": node_name,
                "ip": ip_address,
                "status": "success",
                "country": main_ip_data.get("country", "Unknown"),
                "city": main_ip_data.get("city", "Unknown"),
                "isp": main_ip_data.get("isp", "Unknown"),
                "asn": main_ip_data.get("as", "Unknown")
            })

    ip_version = "IPv6" if ":" in ip_address else "IPv4"
    
    # 4. WHOIS 数据解析
    whois_info = None
    if not is_ip_input:
        try:
            ext = tldextract.extract(target)
            root_domain = f"{ext.domain}.{ext.suffix}"
            if ext.domain and ext.suffix:
                w = whois.whois(root_domain)
                whois_info = {"root_domain": root_domain}
                if w.registrar or w.status:
                    whois_info.update({
                        "mode": "structured",
                        "registrar": w.registrar or "Unknown",
                        "whois_server": w.whois_server or "Unknown",
                        "creation_date": format_date(w.creation_date),
                        "updated_date": format_date(w.updated_date),
                        "expiration_date": format_date(w.expiration_date),
                        "name_servers": format_list(w.name_servers),
                        "status": format_list(w.status),
                        "emails": format_list(w.emails) if w.emails else "Privacy Protected",
                        "dnssec": w.dnssec or "Unsigned"
                    })
                else:
                    whois_info.update({"mode": "raw", "raw_text": w.text or "No raw data"})
        except Exception:
            pass

    # 5. 组装结果 -> 存入缓存 -> 返回
    final_response = {
        "target": target,
        "resolved_ip": ip_address,
        "ip_version": ip_version,
        "multi_dns_details": rich_multi_dns,
        "location": {
            "continent": main_ip_data.get("continent", "Unknown"),
            "country": f"{main_ip_data.get('country', 'Unknown')} ({main_ip_data.get('countryCode', '')})",
            "region": main_ip_data.get("regionName", "Unknown"),
            "city": main_ip_data.get("city", "Unknown"),
            "zip": main_ip_data.get("zip", "N/A") or "N/A",
            "coords": f"{main_ip_data.get('lat', 0)}, {main_ip_data.get('lon', 0)}",
            "timezone": main_ip_data.get("timezone", "Unknown")
        },
        "network": {
            "isp": main_ip_data.get("isp", "Unknown"),
            "org": main_ip_data.get("org", "Unknown"),
            "asn": main_ip_data.get("as", "Unknown"),
            "asname": main_ip_data.get("asname", "Unknown"),
            "reverse": main_ip_data.get("reverse", "") or "N/A"  # 核心修复点：空字符串转 N/A
        },
        "flags": {
            "mobile": main_ip_data.get("mobile", False),
            "proxy": main_ip_data.get("proxy", False),
            "hosting": main_ip_data.get("hosting", False)
        },
        "whois": whois_info
    }

    query_cache.set(cache_key, final_response)
    return final_response