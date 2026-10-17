import os
import requests

ROOM_ID = "22747736"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN") # 从环境变量读取

def main():
    url = f"https://api.live.bilibili.com/room/v1/Room/get_info?id={ROOM_ID}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data["code"] == 0:
            room_data = data["data"]
            if room_data["live_status"] == 1:
                # 检测到开播，发送通知
                send_wechat(room_data["title"], room_data["room_id"])
                print("检测到开播，通知已发送。")
            else:
                print("当前未开播。")
    except Exception as e:
        print(f"请求出错: {e}")

def send_wechat(title, room_id):
    url = "http://www.pushplus.plus/send"
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": "📢 B站直播开播通知",
        "content": f"直播间 {room_id} 正在直播：{title}",
        "template": "html"
    }
    requests.post(url, json=payload, timeout=10)

if __name__ == "__main__":
    main()
