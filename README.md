# hello-bilibili
获取噼哩噼哩弹幕数据

## 1.配置venv环境
### 1.1 初始化venv
```shell
python3 -m venv ./vevn
```
```shell
## windows环境使用这个命令
python3 -m venv .\venv
```
### 1.2 激活venv环境 （激活成功后，命令行前会有 (vevn)  标志）
```shell
## mac环境
source ./venv/bin/activate
```
```shell
## windows环境
.\venv\Scripts\activate
```

## 2.venv环境下安装依赖 (pip  pip3 都可，pip不行试试pip3)
```shell
pip3 install -r requirements.txt
```

## 3.爬取弹幕数据
```shell
python3 crawl.py
```

