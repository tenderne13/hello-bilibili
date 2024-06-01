# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 19:51:21 2024

@author: gnf20
"""


import pandas as pd
import re

# 定义一个清理字符串的函数
def clean_string(s):
    # 移除除了字母、数字、常见标点和中文之外的所有字符
    return re.sub(r'[^\w\s,.!?;:\-()\[\]{}\'\"`~@#%^&+=<>*\u4e00-\u9fff]+', '', str(s))

bvid = input('输入bvid:')

# 读取Excel文件
df = pd.read_csv(f"./{bvid}/{bvid}_弹幕.csv")

# 清理“弹幕”列中的每个字符串
df['弹幕'] = df['弹幕'].apply(clean_string)

# 统计“弹幕”列中相同内容的数量
danmu_counts = df['弹幕'].value_counts().reset_index()
danmu_counts.columns = ['弹幕内容', '数量']

# 将统计结果写入一个新的Excel文件
danmu_counts.to_excel(f'./{bvid}/{bvid}.xlsx', index=False)

