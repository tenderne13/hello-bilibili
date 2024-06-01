import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 设置字体，以便显示中文
#font_path = r"C:\Windows\Fonts\simsun.ttc"  # 指定字体路径，这里使用宋体
font_path = r"/System/Library/Fonts/Hiragino Sans GB.ttc"  # 指定字体路径，这里使用宋体
font_prop = FontProperties(fname=font_path, size=14)
#font_prop = FontProperties(size=14)


bvid = input('输入bvid:')
# 读取数据
df = pd.read_csv(f"./{bvid}/{bvid}_弹幕.csv")

# 处理时间数据
df['时间'] = pd.to_datetime(df['时间'])
# 转换时间为一天中的秒数
df['时间（秒）'] = df['时间'].dt.hour * 60 + df['时间'].dt.minute 
df.set_index('时间（秒）', inplace=True)

# 分组并计算每秒的弹幕数量
barrage_counts_per_second = df.groupby('时间（秒）').size()

# 重置索引，准备计算每日弹幕数量
df.reset_index(inplace=True)
df['发送时间'] = pd.to_datetime(df['发送时间']).dt.date  # 仅保留日期部分
barrage_counts_per_day = df.groupby('发送时间').size()

# 创建两个子图
fig, ax = plt.subplots(2, 1, figsize=(14, 12))
#plt.figure(figsize=(10, 6))
#plt.plot(barrage_counts_per_second.index, barrage_counts_per_second, 'b-o', markersize=1, linewidth=1, label='每秒弹幕数量')
#plt.xlabel('时间（秒）', fontproperties=font_prop)
#plt.ylabel('弹幕数量', fontproperties=font_prop)
#plt.title('每秒弹幕数量的变化趋势', fontproperties=font_prop)
#plt.grid(True)
#plt.legend(prop=font_prop)

# 绘制每秒弹幕数量的折线图
ax[0].plot(barrage_counts_per_second.index, barrage_counts_per_second, 'b-o', markersize=1, linewidth=1, label='每秒弹幕数量')
ax[0].set_xlabel('时间（秒）', fontproperties=font_prop)
ax[0].set_ylabel('弹幕数量', fontproperties=font_prop)
ax[0].set_title('每秒弹幕数量的变化趋势', fontproperties=font_prop)
ax[0].grid(True)
ax[0].legend(prop=font_prop)

#绘制每日弹幕数量的折线图
ax[1].plot(barrage_counts_per_day.index, barrage_counts_per_day, 'r-o', markersize=1, linewidth=1, label='每日弹幕数量')
ax[1].set_xlabel('日期', fontproperties=font_prop)
ax[1].set_ylabel('弹幕数量', fontproperties=font_prop)
ax[1].set_title('每日弹幕数量的变化趋势', fontproperties=font_prop)
ax[1].grid(True)
ax[1].legend(prop=font_prop)

plt.tight_layout()
plt.savefig(f'./{bvid}/{bvid}.png')
plt.show()
