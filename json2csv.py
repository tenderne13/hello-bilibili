# -*- coding: utf-8 -*-
"""
Created on Wed May 29 21:31:38 2024

@author: gnf20
"""

import csv
import json
import logging
import os
import time

# 创建log文件夹
if not os.path.exists('log'):
    os.makedirs('log')

# 配置日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler('log/json2csv.log')
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建格式化器并将其添加到处理器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 获取弹幕api
origin_url = 'https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid={}&date={}'
# 获取月份弹幕索引
month_url = 'https://api.bilibili.com/x/v2/dm/history/index?type=1&oid={}&month={}'

# 全局变量，用于跟踪上一次读取的文件索引
last_file_index = -1


def loadJsonFile(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        logging.info(f"===>加载文件 {file_path} 完成,size: {len(data)}")
    return data

def processJsonData(data,csv_writer):
    row_count = 0
    allData = []
    danmaku_set = set()  # 存储已获取的弹幕
    for item in data:
        retry_count = 1
        for _ in range(retry_count):
            try:
                ctime = get_time(item.get('ctime'))
                message = item.get('content')
                progress = item.get('progress')
                ptime = get_time2(progress)
                danmaku_id = item.get('id')

                if danmaku_id not in danmaku_set:  # 判断弹幕是否已存在
                    csv_writer.writerow([ptime, message, ctime])
                    row_count += 1
                    danmaku_set.add(danmaku_id)
                    allData.append(item)
                break
            except Exception as e:
                #logging.error("处理弹幕错误: %s", e)
                continue
    logging.info(
        f"===>处理 数据完成, csv_文件当前 共有 {row_count} 行数据 ")



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


def crawlData():
    f_path = os.getcwd()
    fnames = os.listdir(f_path)
    bvid = input('输入Bvid：')
    # 如果跟目录没有该文件夹，创建文件夹
    directory = bvid
    if not os.path.exists(directory):
        os.makedirs(directory)

    fname = './' + bvid + '/' + bvid + '_弹幕.csv'
    with open(fname, 'w+', newline='', encoding='utf_8_sig') as f:
        jsonData = loadJsonFile(f"./{bvid}/{bvid}.json")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["时间", "弹幕", "发送时间"])
        processJsonData(jsonData, csv_writer)

if __name__ == '__main__':
    # get_have_danmaku_dates(1507499161)
    crawlData()
