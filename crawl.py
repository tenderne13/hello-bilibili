# -*- coding: utf-8 -*-
"""
Created on Wed May 29 21:31:38 2024

@author: gnf20
"""

import requests
import re
from Bztm_pb2 import DmSegMobileReply
import json
from google.protobuf.json_format import MessageToJson
import csv
import os
import datetime
from tqdm import tqdm
import time
from google.protobuf.message import DecodeError
import random

# 获取弹幕api
origin_url = 'https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid={}&date={}'

# 获取cid
def get_cid(bvid):
    video_url = 'https://www.bilibili.com/video/' + bvid
    page = requests.get(video_url, headers=header).text
    cid = re.search(r'"cid":[0-9]+', page).group()[6:]
    return cid

# 生成日期序列
def create_assist_date(datestart=None, dateend=None):
    if datestart is None:
        datestart = '2024-05-01'
    if dateend is None:
        dateend = datetime.datetime.now().strftime('%Y-%m-%d')

    datestart = datetime.datetime.strptime(datestart, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(dateend, '%Y-%m-%d')
    date_list = []
    date_list.append(datestart.strftime('%Y-%m-%d'))
    while datestart < dateend:
        datestart += datetime.timedelta(days=1)
        date_list.append(datestart.strftime('%Y-%m-%d'))
    return date_list

# 获取日期输入
def get_dates():
    des = input('输入爬取弹幕的“开始日期”：')
    dates = des.split()
    date_list = create_assist_date(dates[0])
    return date_list

# 时间戳转换成日期
def get_time(ctime):
    timeArray = time.localtime(int(ctime))
    otherStyleTime = time.strftime("%Y.%m.%d", timeArray)
    return str(otherStyleTime)

# 时间戳转换成时间
def get_time2(t):
    t1 = float(t) / 1000
    t2 = time.localtime(t1)
    t3 = time.strftime("%M:%S", t2)
    return t3

# 将时间戳转换为毫秒单位
def to_milliseconds(timestamp):
    return timestamp * 1000

if __name__ == '__main__':
    f_path = os.getcwd()
    fnames = os.listdir(f_path)

    # 从根目录init文件中读取cookie
    with open('cookie.init', 'r') as file:
        # 读取文件内容
        cookie = file.read()
    header = {
        'accept': '*/*',
        'Cookie': cookie,
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://www.bilibili.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'referer':'https://www.bilibili.com/'
    }

    bvid = input('输入Bvid：')
    cid = get_cid(bvid)
    dates = get_dates()

    directory = bvid
    if not os.path.exists(directory):
        os.makedirs(directory)
    fname = './'+bvid+'/'+bvid + '_弹幕.csv'
    with open(fname, 'w+', newline='', encoding='utf_8_sig') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["时间", "弹幕", "发送时间"])
        danmaku_set = set()  # 存储已获取的弹幕
        # 声明一个list 存储全量json文件
        allData = []
        for ditem in tqdm(dates):
            url = origin_url.format(cid, ditem)
            retry_count = 3
            for _ in range(retry_count):
                try:
                    html = requests.request(url=url, method='get', headers=header)
                    DM = DmSegMobileReply()
                    DM.ParseFromString(html.content)
                    break
                except DecodeError as e:
                    print("解析错误:", e)
                    continue
            else:
                print(ditem, ':爬取获取数据失败')
                continue
            
            data_json = json.loads(MessageToJson(DM))
            if 'elems' not in data_json:
                print(f"日期 {ditem} 没有弹幕数据")
                continue
            # 追加到全量json文件
            allData += data_json['elems']
            for i in data_json['elems']:
                retry_count = 3
                for _ in range(retry_count):
                    try:
                        ctime = get_time(i['ctime'])
                        message = i['content']
                        ptime = get_time2(i['progress'])
                        milliseconds = to_milliseconds(i['progress']) # 将时间戳转换为毫秒单位
                        danmaku = (milliseconds, message, ctime)
                        if danmaku not in danmaku_set:  # 判断弹幕是否已存在
                            csv_writer.writerow([ptime, message, ctime])
                            danmaku_set.add(danmaku)
                        break
                    except Exception as e:
                        print("处理弹幕错误:", e)
                        continue
                else:
                    print("处理弹幕失败，跳过")
            random_decimal = round(random.uniform(4, 6), 1)
            time.sleep(random_decimal)
        

        # 将json数据写入文件 方便其他方式的分析
        with open(f"./{bvid}/{bvid}.json", 'w', encoding='utf-8') as fjson:
            json.dump(allData, fjson, ensure_ascii=False, indent=4)
        f.close()
