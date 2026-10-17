import os
import requests

# 监控的 B 站直播间 ID（例如: 22747736）
ROOM_ID = "22747736"

# 从 GitHub Secrets 环境变量中读取 Server酱 SendKey
SERVERCHAN_SENDKEY = os.environ.get("SERVERCHAN_SENDKEY")

def main():
    url = f"https://api.live.bilibili.com/room/v1/Room/get_info?id={ROOM_ID}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data["code"] == 0:
            room_data = data["data"]
            # live_status: 1 为直播中
            if room_data["live_status"] == 1:
                title = room_data["title"]
                room_id = room_data["room_id"]
                uname = room_data.get("uname", "主播")
                print(f"检测到开播！标题: {title}")
                send_serverchan_notice(title, uname, room_id)
            else:
                print("当前未开播。")
        else:
            print(f"B站 API 返回异常: {data.get('message')}")
    except Exception as e:
        print(f"请求发生异常: {e}")

def send_serverchan_notice(title, uname, room_id):
    """通过 Server酱 发送微信通知"""
    if not SERVERCHAN_SENDKEY:
        print("错误：未检测到 SERVERCHAN_SENDKEY 环境变量！")
        return

    url = f"https://sctapi.ftqq.com/{SERVERCHAN_SENDKEY}.send"
    live_url = f"https://live.bilibili.com/{room_id}"
    
    # 支持 Markdown 语法
    desp = f"""
### 📢 B站直播间开播提醒

- **主播**：{uname}
- **房间标题**：{title}
- **房间 ID**：{room_id}

[👉 点击这里直接进入直播间]({live_url})
"""

    payload = {
        "title": f"📢 B站开播提醒: {uname} 正在直播",
        "desp": desp
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        res_data = response.json()
        print("Server酱 返回结果：", res_data)
        if res_data.get("code") == 0:
            print("微信推送成功！")
        else:
            print(f"微信推送失败: {res_data.get('info')}")
    except Exception as e:
        print(f"发送 Server酱 通知异常: {e}")

if __name__ == "__main__":
    main()
