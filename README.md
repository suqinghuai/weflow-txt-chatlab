# weflow-txt-chatlab

## 项目介绍

这是一个用于将WeFlow导出的txt格式聊天记录转换为适配ChatLab的jsonl格式的工具，方便导入ChatLab中查看聊天记录。

## 功能特性

- 批量转换当前目录下的所有txt文件
- 自动从文件名提取联系人名称
- 支持识别多种消息类型（文本、图片、视频、语音、表情包、链接等）
- 自动生成符合ChatLab格式的JSONL文件
- 支持多种时间格式（YYYY-MM-DD、YYYY/MM/DD、YYYY.MM.DD）

## 使用方法

### 方法一：使用可执行文件（main.exe）

1. 将 `main.exe` 复制到存放WeFlow导出的txt聊天记录的文件夹中
2. 双击运行 `main.exe`
3. 程序会自动识别并转换所有txt文件
4. 转换完成后，会在同一目录生成对应的.jsonl文件
5. 按任意键退出程序

### 方法二：直接运行Python脚本

1. 确保安装了Python 3.6+
2. 将 `main.py` 复制到存放WeFlow导出的txt聊天记录的文件夹中
3. 在该文件夹中打开命令提示符
4. 运行命令：`python main.py`
5. 程序会自动识别并转换所有txt文件
6. 转换完成后，会在同一目录生成对应的.jsonl文件
7. 按任意键退出程序

## 文件名格式

程序支持以下文件名格式：
- `联系人名称.txt`
- `私聊_联系人名称.txt`

程序会自动从文件名中提取联系人名称，用于生成JSONL文件中的联系人信息。

## 输出文件

转换完成后，程序会在同一目录生成与原txt文件同名但后缀为 `.jsonl` 的文件。例如：
- 输入：`张三.txt`
- 输出：`张三.jsonl`

## 支持的消息类型

| 消息类型 | 识别方式 | JSONL中的type值 |
|---------|---------|---------------|
| 文本 | 普通文本 | 0 |
| 图片 | 以`[图片]`开头 | 2 |
| 视频 | 以`[视频]`开头 | 3 |
| 语音 | 以`[语音]`开头 | 4 |
| 链接 | 包含`[链接]` | 5 |
| 表情包 | 以`[表情包]`或`[表情`开头 | 7 |
| 其他消息 | 以`[其他消息]`开头 | 1 |

## 注意事项

1. 请确保txt文件是由WeFlow导出的聊天记录格式
2. 程序会尝试解析txt文件中的时间戳和发送者信息
3. 如果txt文件格式不符合预期，可能会导致部分消息解析失败
4. 转换后的JSONL文件可以直接导入ChatLab查看

## 示例

### 输入（txt文件）：
```
2023-01-01 12:00:00 "我"
你好！

2023-01-01 12:01:00 "张三"
你好，有什么事吗？

2023-01-01 12:02:00 "我"
[图片]
```

### 输出（jsonl文件）：
```json
{"_type": "header", "chatlab": {"version": "0.0.2", "exportedAt": 1672560000, "generator": "WeFlow"}, "meta": {"name": "张三", "platform": "wechat", "type": "private", "groupAvatar": "https://wx.qlogo.cn/mmhead/ver_1/.../0"}}
{"_type": "member", "platformId": "wxid_...", "accountName": "我", "avatar": "https://wx.qlogo.cn/mmhead/ver_1/.../0"}
{"_type": "member", "platformId": "wxid_...", "accountName": "张三", "avatar": "https://wx.qlogo.cn/mmhead/ver_1/.../0"}
{"_type": "message", "sender": "wxid_...", "accountName": "我", "timestamp": 1672560000, "type": 0, "content": "你好！", "platformMessageId": "1234567890123456789"}
{"_type": "message", "sender": "wxid_...", "accountName": "张三", "timestamp": 1672560060, "type": 0, "content": "你好，有什么事吗？", "platformMessageId": "9876543210987654321"}
{"_type": "message", "sender": "wxid_...", "accountName": "我", "timestamp": 1672560120, "type": 2, "content": "[图片]", "platformMessageId": "1357924680135792468"}
```
## 版本日志

### v1.0.0  2026.4.6
- 初始版本发布，支持基本的txt到jsonl转换功能，通过终端交互

## 常见问题

### Q: 程序运行后提示"在当前目录下未找到txt文件"
A: 请确保 `main.exe` 或 `main.py` 与txt文件在同一目录下，并且txt文件的后缀是 `.txt`

### Q: 转换后的JSONL文件无法导入ChatLab
A: 请检查txt文件格式是否正确，确保时间戳和发送者信息格式符合WeFlow导出的标准格式

### Q: 部分消息没有被转换
A: 可能是因为这些消息的格式不符合解析规则，请检查txt文件中这些消息的格式是否正确

