# bilibili-live-monitor
B站直播间开播推送通知，通过 Server酱 发送微信通知。
- bilibili_live_monitor.py 使用 **GitHub Actions** 定期触发（免费、无需服务器）。
- bilibili_live_monitor_SCF.py 使用 **腾讯云函数** 定期触发（免费、无需服务器）。
- 源代码文件必须放在根目录。

-- --
**一、GitHub Actions配置指南**
- **1. 获取 Server酱 SendKey**
  - 访问 Server酱官网 并登录。
    - 进入 SendKey 页面，复制系统分配给你的 SendKey（通常形如 SCTxxxxxxx...）。
    - 根据页面提示绑定微信公众号（例如“方糖公众号”），以便接收微信消息推送。
    - 通过修改代码，可以适配为Server酱Turbo、Server酱³ 的所有推送通道。
- **2. 配置 GitHub Secrets**
  - 回到你的 GitHub 仓库：
  - 进入 Settings -> Secrets and variables -> Actions。
  - 点击 New repository secret：
    - Name：SERVERCHAN_SENDKEY
    - Secret：填入刚才复制的 SendKey，保存。
- **3.GitHub 仓库的 Actions 权限设置开启“写权限”。**


**二、腾讯云函数控制台配置指南**
- **1.创建函数：**
  - 登录腾讯云函数控制台，点击 新建 -> 空白创建。
  - 函数类型选择：事件函数。
  - 函数名称：bilibili-live-monitor。
  - 运行环境选择：Python 3.9 或 Python 3.10。
  - 把 requests 库打包进项目中
    - 腾讯云函数的开发环境中（或者可以通过终端操作），最直接的解决办法是将 requests 库直接安装到代码所在的当前目录下：
      - 如果你在 Cloud Studio 或远程终端中，直接在项目根目录下运行以下命令：`pip install requests -t .`
      - 或者在本地通过该命令安装好依赖，把整个文件夹（包含 index.py 和生成的 requests 等依赖文件夹）一起压缩成 ZIP 压缩包。回到腾讯云函数控制台，切换为“本地上传zip包”并重新上传。
- **2.配置环境变量：**
  - 在函数的 函数配置 或 环境变量 选项卡中添加两个变量：
    - ROOM_ID：需要监控的B站直播间ID（例如 888888）
    - SERVERCHAN_SENDKEY：你的 Server酱 SendKey
- **3添加定时触发器：**
  - 切换到 触发管理 -> 创建触发器。
  - 触发方式选择：定时触发。
  - 周期/Cron 表达式：输入 */1 * * * *（代表每 1 分钟执行一次）。
- **4.测试运行：**
  - 点击代码编辑页面的 测试 按钮，查看运行日志。
