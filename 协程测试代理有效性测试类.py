"""
本工具从文件中读取代理，测试代理有效性。

#使用协程三部曲：1.在协程入口loop模块中建立loop对象；
# 2.在tasks模块中建立tasks数组，并将协程填进tasks，之后启动协程运行；
# 3.协程对象模块，访问目标页面，将所需数据作为返回值返回。
"""

import aiohttp
import asyncio
from datetime import datetime

headers = {
		# 'Host': 'i.meizitu.net',
		'Pragma': 'no-cache',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
		'Cache-Control': 'no-cache',
		'Connection': 'close',  #需要设置为close：同一个connector应该用不同代理访问目标页面，否则keep-alive的话同一个connector会保持上次的连接(也就必然使用上次的代理)去访问目标页面
		'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 
							Chrome/56.0.2924.87 Safari/537.36''',
		# 'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
		#'Referer': '{}'.format(referer),
	}

#从本地代理库validProxy.txt取出代理
def getLocalProxy():
    with open(r"D:\OneDrive\code\vscode_pythonWorkspace\ProxyObtainer\validProxy.txt",'r') as f:
        return f.read().splitlines()[1:]

#访问目标网站的协程模块，访问httpbin.org/ip，代理成功的话会返回访问者ip（代理ip）
async def getValidProxy(semaphore,session,proxy):
    try:
         async with semaphore:
            async with session.get('http://www.httpbin.org/ip',proxy=proxy,timeout=10) as response:
                html=await response.text()
                ip=proxy[7:proxy.rindex(':')]
                print(ip)
                print(html)
                if response.status==200 and (ip in html):
                    return proxy
                else:return None
    except:
        # print('代理连接失败')
        pass

#tasks模块，提供semaphore（并发数）、connector，组装tasks，并提供并发开始的入口
async def tasksModel(proxies):
    tasks=[]
    semaphore=asyncio.Semaphore(100)    #semaphore限制同时运行协程的数量，类似并发线程数。semaphore有效限制访问速度，测试发现设为100时效比较高
    connector=aiohttp.TCPConnector(limit=100)   #connector并发数，由于不保留连接状态，因此设为多少效果都几乎相同。原理猜测是一个connector发出请求后马上被回收复用，因此实际并发数可能远小于100
    async with aiohttp.ClientSession(headers=headers,connector=connector) as session:
        for proxy in proxies:
            tasks.append(asyncio.ensure_future(getValidProxy(semaphore,session,proxy)))
        await asyncio.gather(*tasks)
    connector.close()
    return tasks
    
#loop模块，建立loop，在loop中启动tasks函数
def main():
    proxies=[
        'http://120.92.88.202:10000',
        'http://119.28.223.103:8088',
        'http://221.225.7.82:61234',
        'http://112.248.20.157:61234',
        'http://121.31.71.29:8123',
        'http://111.155.116.231:8123',
        'http://116.231.61.255:8118',
        'http://183.23.75.190:61234',
        'http://115.225.117.33:8118',
        'http://118.114.77.47:8080',
        'http://42.96.168.79:8888',
        'http://218.93.172.85:6666',
        'http://120.92.88.202:10000',
        'http://120.92.102.240:10000'
    ]

    proxies=getLocalProxy()

    loop=asyncio.get_event_loop()
    tasks=loop.run_until_complete(tasksModel(proxies))      #在loop函数中处理结果，需要tasks函数将tasks作为返回值返回
    loop.close()

    print("有效代理：")
    for task in tasks:
        if task.result():print(task.result())

time_just=datetime.now()
main()
print('time=',datetime.now()-time_just)