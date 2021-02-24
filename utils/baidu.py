import datetime
import hashlib
import re
import time

import requests

import redis

conn = redis.Redis(host='120.78.122.64', password='790623',db=7)

md5 = lambda x:hashlib.md5(x.encode('utf-8')).hexdigest()

url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
appid = '20200530000477540'
appkey = 'ZpDXdRwvjmGEyo3G2XSO'

def genSign(q):
    salt = int(datetime.datetime.now().timestamp())
    value = f'{appid}{q}{salt}{appkey}'
    return salt, md5(value)

def baidu_translate_to_english(q):
    salt, sign = genSign(q)
    data = {
        'q': q,
        'from': 'zh',
        'to':'en',
        'appid':appid,
        'salt':salt,
        'sign':sign
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, headers=headers, data=data)
    try:
        return response.json()['trans_result'][0]['dst']
    except:
        return ''

def translate(word, retry=0):
    if not word:
        return ''
    if retry==3:
        return ''
    key = md5(word)
    try:
        ret = conn.get(key)
        if ret and ret.decode('utf-8').strip():
            return ret.decode('utf-8').strip()
        else:
            pass
    except:
        pass
    try:
        ret = baidu_translate_to_english(word)
        if ret:
            conn.set(key, ret)
            return ret
        else:
            time.sleep(1)
            return translate(word, retry+1)
    except:
        return translate(word, retry+1)

def get_key(key):
    eng = translate(key)
    eng = re.sub(r'[/]',' or ',eng)
    eng = re.sub(r'[\'\",.?\(\)]','',eng)
    words = eng.lower().split(' ')
    snake = '_'.join([x for x in words if x.strip()])
    bigCamel = ''.join([x.capitalize() for x in words])
    littleCamel = bigCamel[0].lower()+bigCamel[1:]
    hungary = f'm{bigCamel}'
    const = snake.upper()
    return [key,littleCamel,bigCamel,hungary,snake,const]

if __name__ == '__main__':
    ret = get_key('联系人姓名')
    print(ret)
