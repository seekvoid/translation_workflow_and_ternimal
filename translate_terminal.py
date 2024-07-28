#!/usr/bin/env python3
# 百度翻译API
# 使用方法 python translate.py --source=auto --to=en --auto=2 --appid=<APP_ID> --secret=<secret> text
# source to auto为可选参数 默认为auto zh 0
# auto = 0时不识别语种，将source翻译到target
# auto = 1时通过百度API识别语种，精确度高，较慢；中译英英译中
# auto = 2时通过首字母判断语种，精确度低，速度较快；中译英英译中

import sys
import requests
import hashlib
import time
import json
import argparse  


# 通用翻译API的URL
URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"
AUTO_URL = "https://fanyi-api.baidu.com/api/trans/vip/language"

# 语种识别, 调用百度API
def recognise(Text: str, appid, salt, sign):

    # 限制长度
    if len(Text) > 100:
        Text = Text[:100]

    # 构造请求参数
    params = {
        "q": Text,
        "appid": appid,
        "salt": salt,
        "sign": sign,
    }

    # 发送请求
    response = requests.get(AUTO_URL, params=params)

    # 解析响应
    result = response.json()

    # 检查结果
    if result["error_msg"] == "success":
        source = result["data"]["src"]
        if source == "en":
            return "zh"
        elif source == "zh":
            return "en"
        else:
            return Target_Language
    else:
        # 失败，fallback default target
        return Target_Language

# 检查是否英文字母开头，用于快速语种识别，不用调用API，提高翻译速度
def is_english_start(s):  
    if not s:  
        return Target_Language
    # 检查首字符的ASCII码是否在英文字符范围内  
    if 65 <= ord(s[0]) <= 90 or 97 <= ord(s[0]) <= 122:
        return "zh"
    else:
        return Target_Language

# 翻译函数
def translate(
    from_lang: str, to_lang: str, q: str, appid: str, secret: str, auto: int
):
    # 生成签名
    salt = int(round(time.time() * 1000))
    sign = appid + q + str(salt) + secret
    sign = hashlib.md5(sign.encode()).hexdigest()

    # 构造请求参数
    params = {
        "q": q,
        "appid": appid,
        "salt": salt,
        "from": from_lang,
        "to": to_lang,
        "sign": sign,
    }

    # 识别语种,中译英,英译中
    if auto == 1:
        params["to"] = recognise(q, appid, salt, sign)
    elif auto == 2:
        params["to"] = is_english_start(q[0])

    # 发送请求
    response = requests.get(URL, params=params)

    # 解析响应
    result = response.json()

    # 检查翻译结果是否存在且不为空
    if "trans_result" in result and result["trans_result"]:
        return result["trans_result"][0]["dst"]
    else:
        # 如果没有翻译结果，则检查是否有错误信息
        if "error_code" in result and result["error_code"] != 52000:
            return result.get("error_msg", "未知错误")
        else:
            return "未知错误"

if __name__ == "__main__":
    # 参数解析
    parser = argparse.ArgumentParser(description='Translate text.')  
    parser.add_argument("--source", type=str, required=False, default="auto" ,help="Source language code")  
    parser.add_argument("--to", type=str, required=False, default="en", help="Target language code")  
    parser.add_argument("--appid", type=str, required=True, help="百度API appid")  
    parser.add_argument("--secret", type=str, required=True, help="百度API secret")  
    parser.add_argument("--auto", type=int, required=False, default=0,help="Target language code")  
    parser.add_argument('text', type=str, help='Text to process')  # 这是一个位置参数  
    args = parser.parse_args()  
   
    # 调用API并返回
    print(translate(args.source, args.to, args.text, args.appid, args.secret, args.auto))
