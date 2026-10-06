# hansilu.py
import requests
import json
import re
from datetime import datetime, timedelta

BASE_URL = "https://xin01.hansilu.fun"

# ---------- 基础 API 函数 ----------
def get_user_id(token):
    url = f"{BASE_URL}/v2/api/user/home"
    headers = {
        "token": token,
        "version": "5.0.7",
        "version-code": "107",
        "content-length": "0",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.11.0",
    }
    resp = requests.post(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取用户ID失败: {data}")
    return data["data"]["id"]

def get_user_detail(token, uid):
    url = f"{BASE_URL}/Api/User/getUserHome"
    headers = {
        "token": token,
        "version": "5.0.7",
        "version-code": "107",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.11.0",
    }
    data = {"uid": uid, "fuid": uid}
    resp = requests.post(url, headers=headers, data=data, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    if result.get("state", {}).get("code") != 0:
        raise Exception(f"获取用户详情失败: {result}")
    return result["data"]

def get_look_record(token, uid, app_type=0, page_size=10, page=1, type=0):
    url = f"{BASE_URL}/Api/Home/getLookRecord"
    headers = {
        "token": token,
        "version": "5.0.7",
        "version-code": "107",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.11.0",
    }
    data = {
        "uid": uid,
        "app_type": app_type,
        "pageSize": page_size,
        "page": page,
        "type": type,
    }
    resp = requests.post(url, headers=headers, data=data, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    if result.get("state", {}).get("code") != 0:
        raise Exception(f"获取浏览记录失败: {result}")
    return result

def get_user_settings(token):
    url = f"{BASE_URL}/v2/api/user/settings"
    headers = {
        "token": token,
        "version": "5.0.7",
        "version-code": "107",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.11.0",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取用户设置失败: {data}")
    return data["data"]

def set_user_settings(token, auth_token, chat_token, website_token):
    url = f"{BASE_URL}/v2/api/user/settingsset"
    headers = {
        "token": token,
        "version": "5.0.7",
        "version-code": "107",
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.11.0",
    }
    payload = {
        "authToken": auth_token,
        "chatToken": chat_token,
        "websiteToken": website_token,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") != 0:
        raise Exception(f"更新用户设置失败: {result}")
    return result

def get_sign_in_date(token, uid):
    url = f"{BASE_URL}/Api/Home/getSignInDate"
    headers = {
        "token": token,
        "version": "5.0.7",
        "version-code": "107",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.11.0",
    }
    data = {"uid": uid}
    resp = requests.post(url, headers=headers, data=data, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    if result.get("state", {}).get("code") != 0:
        raise Exception(f"获取签到日期失败: {result}")
    return result.get("data", [])

def sign_in(token, uid):
    url = f"{BASE_URL}/Api/Home/signIn"
    headers = {
        "token": token,
        "version": "5.0.7",
        "version-code": "107",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.11.0",
    }
    data = {"uid": uid}
    resp = requests.post(url, headers=headers, data=data, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    if result.get("state", {}).get("code") != 0:
        raise Exception(f"签到失败: {result}")
    return result.get("data", {})

def get_sign_rules(token, type=10):
    url = f"{BASE_URL}/Api/Public/pageContent"
    headers = {
        "token": token,
        "version": "5.0.7",
        "version-code": "107",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.11.0",
    }
    data = {"type": type}
    resp = requests.post(url, headers=headers, data=data, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    if result.get("state", {}).get("code") != 0:
        raise Exception(f"获取页面内容失败: {result}")
    html_content = result.get("data", {}).get("content", "")
    text = re.sub(r'<[^>]+>', ' ', html_content)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    rules = []
    pattern = re.compile(r'连续签到(\d+)天奖励([\d]+)([^\d\s]+)')
    for line in lines:
        match = pattern.search(line)
        if match:
            days = int(match.group(1))
            amount = match.group(2)
            unit = match.group(3).strip()
            reward = f"{amount}{unit}"
            rules.append({"days": days, "reward": reward})
    return rules

# ---------- 组合处理 ----------
def process_user(token):
    result = {
        "token": token,
        "success": False,
        "uid": None,
        "user_info": {},
        "settings": {},
        "sign_in_today": False,
        "sign_in_reward": {},
        "sign_rules": [],
        "total_sign_days": 0,
        "continuous_days": 0,
        "next_reward_days": 0,
        "next_reward_info": "",
        "error": None
    }
    try:
        uid = get_user_id(token)
        result["uid"] = uid

        detail = get_user_detail(token, uid)
        user_info = detail.get("user", {})
        result["user_info"] = {
            "nickname": user_info.get("name"),
            "email": user_info.get("email"),
            "phone": user_info.get("phone"),
            "grade": user_info.get("grade_name"),
            "integral": user_info.get("integral"),
            "exp": user_info.get("exp"),
        }

        settings = get_user_settings(token)
        result["settings"] = {
            "authToken": settings.get("authToken"),
            "chatToken": settings.get("chatToken"),
            "websiteToken": settings.get("websiteToken"),
        }

        # 签到相关
        signed_dates = get_sign_in_date(token, uid)
        today = datetime.now().strftime("%Y-%m-%d")
        signed_set = set(signed_dates)

        result["total_sign_days"] = len(signed_dates)

        # 计算连续签到天数
        continuous = 0
        check_date = datetime.now()
        while True:
            date_str = check_date.strftime("%Y-%m-%d")
            if date_str in signed_set:
                continuous += 1
                check_date -= timedelta(days=1)
            else:
                break
        result["continuous_days"] = continuous

        # 执行签到
        if today in signed_set:
            result["sign_in_today"] = True
            result["sign_in_reward"] = {"msg": "今日已签到"}
        else:
            reward = sign_in(token, uid)
            result["sign_in_today"] = True
            result["sign_in_reward"] = reward

        # 获取签到规则并计算下一个奖励
        rules = get_sign_rules(token)
        result["sign_rules"] = rules
        sorted_rules = sorted(rules, key=lambda x: x['days'])
        next_reward = None
        for rule in sorted_rules:
            if rule['days'] > continuous:
                next_reward = rule
                break
        if next_reward:
            result["next_reward_days"] = next_reward['days'] - continuous
            result["next_reward_info"] = f"奖励 {next_reward['reward']}"
        else:
            # 检查当前连续天数是否匹配某个规则
            matched_rule = None
            for rule in sorted_rules:
                if rule['days'] == continuous:
                    matched_rule = rule
                    break
            if matched_rule:
                result["next_reward_days"] = 0
                result["next_reward_info"] = f"已获得连续签到 {continuous} 天奖励（{matched_rule['reward']}）"
            else:
                result["next_reward_days"] = 0
                result["next_reward_info"] = "已达成所有签到奖励"

        result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result