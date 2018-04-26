import asyncio
import aiohttp

headers = {
		'Pragma': 'no-cache',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
		'Cache-Control': 'no-cache',
		'Connection': 'close',
		'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 
							Chrome/56.0.2924.87 Safari/537.36'''
}

#该函数身份是loop模块。用同一个loop连续两次进行验证。
def filterValidProxies(proxyList):
    proxyList=arrangeProxyForCoroutine(proxyList)
    print('正在验证代理有效性')
    validProxyList=[]
    loop=asyncio.get_event_loop()
    tasks=loop.run_until_complete(getValidProxy(proxyList))
    for task in tasks:
        if task.result():validProxyList.append(task.result())
    print('从代理网站抓取到的有效代理数量：'+str(len(validProxyList)))

    #doublecheck
    doubleCheckedProxyList=[]
    loop=asyncio.get_event_loop()
    tasks=loop.run_until_complete(doubleCheckProxy(validProxyList))
    for task in tasks:
        if task.result():doubleCheckedProxyList.append(task.result())
    print('doubleCheck有效代理数量：'+str(len(doubleCheckedProxyList)))
    loop.close()
    return doubleCheckedProxyList

#tasks模块。建立taskslist，建立协程，包装成future对象塞进list。全部协程执行完后将taskslist返回给loop模块
async def getValidProxy(proxyList):
    tasks=[]
    semaphore=asyncio.Semaphore(100)
    connector=aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(headers=headers,connector=connector) as session:
        for proxy in proxyList:
            tasks.append(asyncio.ensure_future(visitHttpbinReturnValidProxy(semaphore,session,proxy)))
        await asyncio.gather(*tasks)
    connector.close()
    return tasks

#协程模块，负责访问httpbin.org/ip，访问成功的话html会包含代理ip，如果ip in html为Ture则说明代理有效
async def visitHttpbinReturnValidProxy(semaphore,session,proxy):
    try:
        async with semaphore:
            async with session.get('http://www.httpbin.org/ip',proxy=proxy,timeout=10) as response:
                html=await response.text()
                ip=proxy[7:proxy.rindex(':')]
                if response.status==200 and (ip in html):
                    return proxy
                else:return None
    except:
        # print('代理连接失败')
        pass

#对第一次选出的有效代理进行二次检查，访问MA，有效代理准备入库
#二次检查最好直接访问待爬取的网站
async def doubleCheckProxy(validProxyList):
    print('正在二次验证代理有效性')
    tasks=[]
    semaphore=asyncio.Semaphore(100)
    connector=aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(headers=headers,connector=connector) as session:
        for proxy in validProxyList:
            tasks.append(asyncio.ensure_future(doubleCheckReturnValidProxy(semaphore,session,proxy)))
        await asyncio.gather(*tasks)
    connector.close()
    return tasks

#doublecheck的协程对象，doublecheck时最好访问真实需访问的页面，即需要修改该函数
async def doubleCheckReturnValidProxy(semaphore,session,proxy):
    doubleCheckUrl='http://www.metal-archives.com/bands//'+'1'
    try:
        async with semaphore:
            async with session.get(doubleCheckUrl,proxy=proxy,timeout=20) as response:
                html=await response.text()
                if response.status==200:return proxy
                else:return None
    except:
        pass

#现在收集到的proxy都保持[[协议,ip,端口],[]]的格式，本函数是专门使用协程验证代理有效性，
#因此本函数将原始proxy的格式改为[http:??111.222:8080,http://222.333:8080]的格式，专供协程使用。
def arrangeProxyForCoroutine(proxyList):
    arrangedList=[]
    for proxy in proxyList:
        arrangedList.append(proxy[0]+'://'+proxy[1]+':'+proxy[2])
    return arrangedList

if __name__=='__main__':
    proxyList=[
        ['http','61.180.149.162','61202'],
        ['http','60.166.48.204','61202'],
        ['http','1.197.88.101','61202'],
    ]
    validList=filterValidProxies(proxyList)
    for item in validList:
        print(item)