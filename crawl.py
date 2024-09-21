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
from dateutil.relativedelta import relativedelta
import logging

# 创建log文件夹
if not os.path.exists('log'):
    os.makedirs('log')

# 配置日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler('log/crawl.log')
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


def getHeader():
    global last_file_index
    cookie_files = ['cookie.init', 'cookie2.init']

    # 切换到下一个文件
    last_file_index = (last_file_index + 1) % len(cookie_files)
    file_name = cookie_files[last_file_index]

    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            cookie = file.read().strip()
            if not cookie:
                raise ValueError(f"{file_name} 文件为空")
    else:
        raise FileNotFoundError(f"{file_name} 文件未找到")
    header = {
        'accept': '*/*',
        'Cookie': cookie,
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://www.bilibili.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'referer': 'https://www.bilibili.com/'
    }
    return header


header = getHeader()


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


# 生成月份序列
def create_month_date(datestart=None, dateend=None):
    if datestart is None:
        datestart = '2019-09'
    if dateend is None:
        dateend = datetime.datetime.now().strftime('%Y-%m')

    datestart = datetime.datetime.strptime(datestart, '%Y-%m')
    dateend = datetime.datetime.strptime(dateend, '%Y-%m')
    finalList = []
    while datestart <= dateend:
        finalList.append(datestart.strftime('%Y-%m'))
        # 延后一个月
        datestart += relativedelta(months=1)
    logging.info("==> 所有的月份：%s", finalList)
    return finalList


# 获取日期输入
def get_dates():
    des = input('输入爬取弹幕的 开始月份”：')
    dates = des.split()
    date_list = create_assist_date(dates[0])
    return date_list


# 获取当前月有弹幕的日期
def get_have_danmaku_dates(oid):
    des = input('输入爬取弹幕的 开始月份”：')
    dates = des.split()
    monthList = create_month_date(dates[0])
    have_danmaku_dates = []
    for item in monthList:
        try:
            url = month_url.format(oid, item)
            logging.info(f"===>请求url：{url}")
            header = getHeader()
            resp = requests.request(url=url, method='get', headers=header)
            data_json = json.loads(resp.text)
            have_danmaku_dates += data_json['data']
        except Exception as e:
            logging.error("请求失败：%s", e)
            continue
        random_decimal = round(random.uniform(1, 2), 1)
        logging.info(f"休息{random_decimal} 秒防止被封掉 cookieID index: {last_file_index}")
        time.sleep(random_decimal)
    logging.info(f"==> 所有 有弹幕的日期：{have_danmaku_dates}")
    return have_danmaku_dates


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

    header = getHeader()
    bvid = input('输入Bvid：')
    cid = get_cid(bvid)
    logging.info(f"===>cid:{cid}")
    dates = get_have_danmaku_dates(cid)

    # 如果跟目录没有该文件夹，创建文件夹
    directory = bvid
    if not os.path.exists(directory):
        os.makedirs(directory)

    fname = './' + bvid + '/' + bvid + '_弹幕.csv'
    with open(fname, 'w+', newline='', encoding='utf_8_sig') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["时间", "弹幕", "发送时间"])
        row_count = 0
        danmaku_set = set()  # 存储已获取的弹幕
        # 声明一个list 存储全量json文件
        allData = []
        for ditem in tqdm(dates):
            #logging.info(f"===>获取日期：{ditem}, cookieID index: {last_file_index}")
            url = origin_url.format(cid, ditem)
            retry_count = 3
            for _ in range(retry_count):
                try:
                    header = getHeader()
                    html = requests.request(url=url, method='get', headers=header)
                    DM = DmSegMobileReply()
                    DM.ParseFromString(html.content)
                    break
                except DecodeError as e:
                    logging.info("解析错误:", e)
                    continue
            else:
                logging.info(ditem, ':爬取获取数据失败')
                continue

            data_json = json.loads(MessageToJson(DM))
            if 'elems' not in data_json:
                logging.info(f"日期 {ditem} 没有弹幕数据")
                continue
            else:
                logging.info(f"日期 {ditem} 有 {len(data_json['elems'])} 条弹幕数据")
            # 追加到全量json文件
            #allData += data_json['elems']
            for item in data_json['elems']:
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
                #else:
                    #logging.info(f"处理弹幕失败，跳过 {item['id']} - {progress}- {message}")
            random_decimal = round(random.uniform(4, 6), 1)
            logging.info(f"===>获取日期：{ditem} 数据完成, csv_文件当前 共有 {row_count} 行数据 ,休息 {random_decimal} 秒, 防止被封ip, cookieID index: {last_file_index}")
            #logging.info(f"休息 : {random_decimal} 秒,防止被噼哩噼哩 封ip, cookieID index: {last_file_index}")
            time.sleep(random_decimal)

        # 将json数据写入文件 方便其他方式的分析
        with open(f"./{bvid}/{bvid}.json", 'w', encoding='utf-8') as fjson:
            json.dump(allData, fjson, ensure_ascii=False, indent=4)
        f.close()
        logging.info(f"===>allData 当前有 {len(allData)} 条数据")
        logging.info(f"**********csv_文件 共有 {row_count} 行数据")
        logging.info(f"===>{bvid} 所有弹幕数据爬取完成<====")


if __name__ == '__main__':
    # get_have_danmaku_dates(1507499161)
    crawlData()
