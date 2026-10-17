import os
import requests

# 监控的 B 站直播间 ID（例如: 22747736）
ROOM_ID = "22747736"

# 从 GitHub Secrets 环境变量中读取 WxPusher 的凭证
WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID")

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
                send_wxpusher_notice(title, uname, room_id)
            else:
                print("当前未开播。")
        else:
            print(f"B站 API 返回异常: {data.get('message')}")
    except Exception as e:
        print(f"请求发生异常: {e}")

def send_wxpusher_notice(title, uname, room_id):
    """通过 WxPusher 发送微信通知"""
    if not WXPUSHER_APP_TOKEN or not WXPUSHER_UID:
        print("错误：未检测到 WXPUSHER_APP_TOKEN 或 WXPUSHER_UID 环境变量！")
        return

    url = "https://wxpusher.zhengjie.chat/api/send/message"
    live_url = f"https://live.bilibili.com/{room_id}"
    
    # 支持 HTML 格式排版
    content = f"""
    <h2>📢 B站直播间开播提醒</h2>
    <p><b>主播：</b>{uname}</p>
    <p><b>房间标题：</b>{title}</p>
    <p><b>房间 ID：</b>{room_id}</p>
    <p><a href="{live_url}">点击这里直接进入直播间</a></p>
    """

    payload = {
        "appToken": WXPUSHER_APP_TOKEN,
        "content": content,
        "contentType": 2,  # 2 表示 HTML 格式
        "uids": [WXPUSHER_UID],
        "url": live_url    # 点击通知直接跳转
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        print("WxPusher 返回结果：", res_data)
        if res_data.get("code") == 1000:
            print("微信推送成功！")
        else:
            print(f"微信推送失败: {res_data.get('msg')}")
    except Exception as e:
        print(f"发送微信通知异常: {e}")

if __name__ == "__main__":
    main()
