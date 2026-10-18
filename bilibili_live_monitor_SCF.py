import os
import requests

# 腾讯云函数的唯一可写目录
STATUS_FILE = "/tmp/live_status.txt"

def get_last_status():
    """读取上一次记录的状态 (1 为已开播并提醒，0 为未开播)"""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return f.read().strip() == "1"
        except Exception:
            return False
    return False

def set_last_status(is_live):
    """保存当前状态到临时文件"""
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            f.write("1" if is_live else "0")
    except Exception as e:
        print(f"写入状态文件失败: {e}")

def send_serverchan_notice(title, room_id, serverchan_sendkey):
    """通过 Server酱 发送微信通知"""
    if not serverchan_sendkey:
        print("错误：未检测到 SERVERCHAN_SENDKEY 环境变量！")
        return

    url = f"https://sctapi.ftqq.com/{serverchan_sendkey}.send"
    live_url = f"https://live.bilibili.com/{room_id}"
    
    desp = f"""
### 📢 B站直播间开播提醒

- **房间标题**：{title}
- **房间 ID**：{room_id}

[👉 点击这里直接进入直播间]({live_url})
"""

    payload = {
        "title": f"📢 B站开播提醒: 直播间 {room_id} 正在直播",
        "desp": desp
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        res_data = response.json()
        print("Server酱 返回结果：", res_data)
    except Exception as e:
        print(f"发送 Server酱 通知异常: {e}")

def main_handler(event, context):
    """腾讯云函数入口函数"""
    # 从云函数环境变量中读取配置
    room_id_str = os.environ.get("ROOM_ID", "22747736")
    serverchan_sendkey = os.environ.get("SERVERCHAN_SENDKEY", "")
    
    url = f"https://api.live.bilibili.com/room/v1/Room/get_info?id={room_id_str}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://live.bilibili.com/{room_id_str}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data["code"] == 0:
            room_data = data["data"]
            live_status = room_data["live_status"]  # 1 为直播中
            title = room_data["title"]
            room_id = room_data["room_id"]
            
            is_live_now = (live_status == 1)
            was_live_last_time = get_last_status()
            
            if is_live_now:
                if not was_live_last_time:
                    print(f"检测到新开播！标题: {title}")
                    send_serverchan_notice(title, room_id, serverchan_sendkey)
                    set_last_status(True)
                else:
                    print("直播进行中（已提醒过，跳过推送）。")
            else:
                if was_live_last_time:
                    print("检测到已下播，重置状态。")
                else:
                    print("当前未开播。")
                set_last_status(False)
        else:
            print(f"B站 API 返回业务异常，错误码: {data.get('code')}, 消息: {data.get('message')}")
    except Exception as e:
        print(f"请求发生异常: {e}")
        
    return "Check finished"
