import pandas as pd
from pyecharts.charts import Line
from pyecharts import options as opts
import json

    
def combine_charts_data(comment):
    tempObj = {
                "showupTime": comment.get('progress',0) / 1000,
                "timestamp" : comment.get('ctime'),
                "comments" : comment.get('content')
            }
    return tempObj

def genRenderFile(bvid):

    with open(f'./{bvid}/{bvid}.json', 'r') as file:
        # 读取文件内容
        commentData = file.read()


    commentData = json.loads(commentData)
    # 将 commentData  转化为json对象，遍历调用 combine_charts_data方法，放入 commentList 中
    commentList = [combine_charts_data(comment) for comment in commentData]
    
    # 将数据转换为pandas DataFrame
    df = pd.DataFrame(commentList)
    # 将showupTime转换为数值类型
    df['showupTime'] = pd.to_numeric(df['showupTime'])
    # 将showupTime分配到10秒的时间段
    df['timeBucket'] = (df['showupTime'] // 10) * 10
    # 对时间段进行分组并计算频次
    frequency = df['timeBucket'].value_counts().sort_index()
    # 创建ECharts折线图
    line = Line()
    # 添加X轴和Y轴数据
    line.add_xaxis(frequency.index.astype(str).tolist())
    line.add_yaxis("频次", frequency.values.tolist())

    # 设置图表标题和坐标轴标签
    line.set_global_opts(title_opts=opts.TitleOpts(title="弹幕变化趋势"),
                        xaxis_opts=opts.AxisOpts(name="时间（秒）"),
                        yaxis_opts=opts.AxisOpts(name="弹幕数量"))

    # 渲染图表到文件（也可以直接在Jupyter Notebook中显示）
    line.render(f'./{bvid}/{bvid}.html')
    return


# 931347350 1507499161
#save_danmu_comments(1507499161)
genRenderFile('BV17m421T7GH')
