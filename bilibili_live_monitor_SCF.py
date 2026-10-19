from datetime import datetime, time
import os
import requests
from urllib.parse import quote

# 优先从环境变量中读取配置
ROOM_ID = int(os.environ.get("ROOM_ID", 22747736))
SERVERCHAN_SENDKEY = os.environ.get("SERVERCHAN_SENDKEY", "")
ANCHOR_NAME = "3DM主播"

# 勿扰模式配置（格式如 "23:00" 和 "07:00"，留空则不启用勿扰）
DND_START = os.environ.get("DND_START", "")
DND_END = os.environ.get("DND_END", "")

# 简易状态记录
_last_live_status = None


def send_serverchan_notification(title, content):
  """发送 Server酱 微信推送通知"""
  if not SERVERCHAN_SENDKEY:
    print("错误：未检测到 SERVERCHAN_SENDKEY 环境变量，无法发送微信通知！")
    return

  encoded_title = quote(title)
  encoded_content = quote(content)
  url = f"https://sctapi.ftqq.com/{SERVERCHAN_SENDKEY}.send?title={encoded_title}&desp={encoded_content}"

  try:
    response = requests.get(url, timeout=5)
    print("Server酱 推送响应:", response.json())
  except Exception as e:
    print(f"发送 Server酱 通知异常: {e}")


def check_dnd_time():
  """检查当前是否处于勿扰时间段内"""
  if not DND_START or not DND_END:
    return False

  try:
    now_time = datetime.now().time()
    start_time = datetime.strptime(DND_START, "%H:%M").time()
    end_time = datetime.strptime(DND_END, "%H:%M").time()

    # 处理跨越午夜的情况（例如 23:00 到次日 07:00）
    if start_time > end_time:
      is_dnd = now_time >= start_time or now_time <= end_time
    else:
      is_dnd = start_time <= now_time <= end_time

    if is_dnd:
      print(
          f"当前时间 {now_time.strftime('%H:%M:%S')} 处于勿扰模式 ({DND_START} ~"
          " 内)，跳过本次轮询。"
      )
      return True
  except Exception as e:
    print(f"勿扰时间解析异常: {e}")

  return False


def main_handler(event, context):
  global _last_live_status

  # 1. 优先检查勿扰模式
  if check_dnd_time():
    return "DND Skipped"

  url = (
      f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={ROOM_ID}"
  )
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  try:
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()

    if data.get("code") == 0:
      room_info = data["data"]
      live_status = room_info["live_status"]  # 1: 直播中, 0: 未开播
      room_title = room_info["title"]
      live_time_str = room_info["live_time"]

      print(
          f"当前状态检查：room_id = {ROOM_ID}, live_status = {live_status},"
          f" 标题 = {room_title}, 开播时间 = {live_time_str}"
      )

      if live_status == 1:
        # 智能防重复判断：结合绝对开播时间，防止云函数冷启动导致状态重置引发重复推送
        is_really_new = False
        try:
          live_time_dt = datetime.strptime(live_time_str, "%Y-%m-%d %H:%M:%S")
          now_dt = datetime.now()
          diff_seconds = (now_dt - live_time_dt).total_seconds()
          print(f"距离该场次开播已过去: {diff_seconds:.1f} 秒")

          if diff_seconds <= 180 and _last_live_status != 1:
            is_really_new = True
        except Exception as ex:
          print(f"解析时间异常: {ex}")
          if _last_live_status != 1:
            is_really_new = True

        if is_really_new and _last_live_status != 1:
          push_title = f"🚨 {ANCHOR_NAME} 开播啦！"
          push_content = (
              f"直播间标题：{room_title}\n\n[点击进入直播间](https://live.bilibili.com/{ROOM_ID})"
          )
          send_serverchan_notification(push_title, push_content)
          _last_live_status = 1
        else:
          print("直播进行中（或属于容器冷启动恢复），非新开播，跳过重复推送。")
          _last_live_status = 1
      else:
        if _last_live_status == 1:
          print("检测到已下播，重置状态。")
        else:
          print("当前未开播。")
        _last_live_status = 0
    else:
      print(f"B站 API 返回业务异常，错误码：{data.get('code')}")

  except Exception as e:
    print(f"请求发生异常: {e}")

  return "Check finished"
