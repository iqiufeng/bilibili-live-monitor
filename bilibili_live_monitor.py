import os
import requests

# 监控的 B 站直播间 ID（例如: 22747736）
ROOM_ID = "22747736"

# 从 GitHub Secrets 环境变量中读取 Server酱 SendKey
SERVERCHAN_SENDKEY = os.environ.get("SERVERCHAN_SENDKEY")

def main():
    # 使用新版 xlive 接口，可以一次性完整获取直播状态、标题和准确的主播昵称
    url = f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={ROOM_ID}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data["code"] == 0:
            room_data = data["data"]["room_info"]
            anchor_data = data["data"]["anchor_info"]["base_info"]
            
            live_status = room_data["live_status"]  # 1 为直播中
            title = room_data["title"]
            room_id = room_data["room_id"]
            uname = anchor_data.get("uname", "未知主播")
            
            if live_status == 1:
                print(f"检测到开播！主播: {uname}, 标题: {title}")
                send_serverchan_notice(title, uname, room_id)
            else:
                print(f"当前未开播。（当前主播：{uname}）")
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
