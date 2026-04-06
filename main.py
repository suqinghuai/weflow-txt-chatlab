import re
import json
import time
import random
import os
import sys
from datetime import datetime
from pathlib import Path

def parse_txt_file(txt_path):
    """解析txt格式的聊天记录"""
    messages = []
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # 尝试匹配时间戳和发送者
        timestamp_match = re.search(r'(\d{4}[-/\.]\d{2}[-/\.]\d{2} \d{2}:\d{2}:\d{2})', line)
        if timestamp_match:
            timestamp_str = timestamp_match.group(1)
            # 提取发送者（从时间戳之后的部分提取）
            # 先移除时间戳部分，再匹配发送者
            line_after_timestamp = line[timestamp_match.end():].strip()
            # 匹配带引号或不带引号的发送者名称
            sender_match = re.search(r'(?:[\'"](.*?)[\'"]|([^\s]+))', line_after_timestamp)
            if sender_match:
                # 提取发送者，优先使用带引号的捕获组
                sender = sender_match.group(1) if sender_match.group(1) else sender_match.group(2)
                # 提取消息内容（下一行开始）
                content = []
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    # 如果下一行是新的消息（有时间戳），则停止
                    if re.search(r'\d{4}[-/\.]\d{2}[-/\.]\d{2} \d{2}:\d{2}:\d{2}', next_line):
                        break
                    if next_line:
                        content.append(next_line)
                    i += 1
                
                # 解析时间戳
                try:
                    # 尝试不同的时间格式
                    if '-' in timestamp_str:
                        dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    elif '/' in timestamp_str:
                        dt = datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
                    elif '.' in timestamp_str:
                        dt = datetime.strptime(timestamp_str, '%Y.%m.%d %H:%M:%S')
                    else:
                        # 无法解析的时间格式，跳过
                        continue
                    
                    timestamp = int(dt.timestamp())
                    
                    # 构建消息对象
                    message = {
                        'sender': sender,
                        'content': '\n'.join(content),
                        'timestamp': timestamp
                    }
                    messages.append(message)
                except Exception as e:
                    # 时间解析失败，跳过
                    i += 1
                    continue
            else:
                # 没有找到发送者，跳过
                i += 1
                continue
        else:
            # 没有找到时间戳，跳过
            i += 1
            continue
    
    return messages

def get_message_type(content):
    """根据消息内容判断消息类型"""
    if content.startswith('[图片]'):
        return 2  # 图片
    elif content.startswith('[视频]'):
        return 3  # 视频
    elif content.startswith('[语音]'):
        return 4  # 语音
    elif content.startswith('[表情包]') or content.startswith('[表情'):
        return 7  # 表情包
    elif content.startswith('[其他消息]'):
        return 1  # 其他消息
    elif '[链接]' in content:
        return 5  # 链接
    else:
        return 0  # 文本

def generate_platform_id():
    """生成随机的platformId"""
    return f"wxid_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))}"

def generate_message_id():
    """生成随机的platformMessageId"""
    return str(random.randint(1000000000000000000, 9999999999999999999))

def generate_avatar_url():
    """生成随机的头像URL"""
    # 生成随机的头像URL，格式与微信头像URL类似
    random_hash = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=64))
    return f"https://wx.qlogo.cn/mmhead/ver_1/{random_hash}/0"

def convert_to_jsonl(txt_path, jsonl_path, contact_name):
    """转换txt文件到jsonl文件"""
    messages = parse_txt_file(txt_path)
    
    if not messages:
        print("没有找到消息记录")
        return
    
    # 获取所有发送者
    senders = set(msg['sender'] for msg in messages)
    
    # 为发送者分配ID
    my_id = generate_platform_id()  # 随机生成自己的ID
    contact_id = generate_platform_id()  # 随机生成对方的ID
    
    sender_to_id = {}
    sender_to_avatar = {}
    
    # 随机生成头像URL
    default_avatar = generate_avatar_url()
    my_avatar = generate_avatar_url()
    
    for sender in senders:
        if sender == '我':
            sender_to_id[sender] = my_id
            sender_to_avatar[sender] = my_avatar
        else:
            sender_to_id[sender] = contact_id
            sender_to_avatar[sender] = default_avatar
    
    # 生成jsonl内容
    jsonl_lines = []
    
    # 1. Header
    header = {
        "_type": "header",
        "chatlab": {
            "version": "0.0.2",
            "exportedAt": int(time.time()),
            "generator": "WeFlow"
        },
        "meta": {
            "name": contact_name,
            "platform": "wechat",
            "type": "private",
            "groupAvatar": default_avatar
        }
    }
    jsonl_lines.append(json.dumps(header, ensure_ascii=False))
    
    # 2. Members
    # 自己
    member_me = {
        "_type": "member",
        "platformId": my_id,
        "accountName": "我",
        "avatar": my_avatar
    }
    jsonl_lines.append(json.dumps(member_me, ensure_ascii=False))
    
    # 对方
    member_contact = {
        "_type": "member",
        "platformId": contact_id,
        "accountName": contact_name,
        "avatar": default_avatar
    }
    jsonl_lines.append(json.dumps(member_contact, ensure_ascii=False))
    
    # 3. Messages
    for msg in messages:
        message_type = get_message_type(msg['content'])
        
        message = {
            "_type": "message",
            "sender": sender_to_id[msg['sender']],
            "accountName": msg['sender'],
            "timestamp": msg['timestamp'],
            "type": message_type,
            "content": msg['content'],
            "platformMessageId": generate_message_id()
        }
        jsonl_lines.append(json.dumps(message, ensure_ascii=False))
    
    # 写入文件
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(jsonl_lines))
    
    print(f"转换完成！")
    print(f"共处理 {len(messages)} 条消息")
    print(f"输出文件: {jsonl_path}")

def main():
    # 获取当前脚本/可执行文件所在目录
    # 处理pyinstaller打包的情况
    if getattr(sys, 'frozen', False):
        # 打包成exe时
        script_dir = os.path.dirname(sys.executable)
    else:
        # 直接运行脚本时
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 查找脚本目录下的所有txt文件
    txt_files = [f for f in os.listdir(script_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print("在当前目录下未找到txt文件")
        input("\n按任意键退出...")
        return
    
    print(f"找到 {len(txt_files)} 个txt文件，开始转换...\n")
    
    # 遍历所有txt文件并转换
    for selected_txt in txt_files:
        txt_file = os.path.join(script_dir, selected_txt)
        
        # 生成输出文件路径（将.txt改为.jsonl）
        jsonl_file = os.path.join(script_dir, selected_txt.replace('.txt', '.jsonl'))
        
        # 从文件名中提取联系人名称（移除前缀和扩展名）
        # 假设文件名为 "私聊_联系人名称.txt" 或 "联系人名称.txt"
        contact_name = selected_txt.replace('.txt', '')
        if '_' in contact_name:
            contact_name = contact_name.split('_', 1)[-1]
        
        print(f"正在转换文件：{selected_txt}")
        print(f"输出文件：{os.path.basename(jsonl_file)}")
        print(f"联系人名称：{contact_name}")
        
        # 执行转换
        convert_to_jsonl(txt_file, jsonl_file, contact_name)
        print()
    
    print(f"所有文件转换完成！共处理 {len(txt_files)} 个文件")
    # 等待用户输入任意值退出
    input("\n按任意键退出...")

if __name__ == "__main__":
    main()