from concurrent.futures import process,thread
from multiprocessing import Manager
import psutil
from urllib import request

headers = {
		'Pragma': 'no-cache',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
		'Cache-Control': 'no-cache',
		'Connection': 'close',
		'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 
							Chrome/56.0.2924.87 Safari/537.36'''
}

#多进程+多线程对每个代理连续两次进行验证。
def filterValidProxiesMultiThreads(proxyList):
    proxyList=arrangeProxyList(proxyList)   #将代理整理为[{'protocal':'ip+:+port'},{'protocal':'ip+:+port'},...]形式
    print('正在使用多进程+多线程验证代理有效性')
    validProxyList=[]

    cpuCoreNumber=psutil.cpu_count(logical=False)   #multiprocessing的cpu_cout()获得的是cpu线程数，psutil才能获得物理核心数
    print('物理核心数：%s'%cpuCoreNumber)
    q=Manager().Queue()
    #根据cpu物理核心数分配资源。设物理核心数n，前n-1次分配(长度/核心数)个资源(每次segment个)，第n次分配其余所有资源
    with process.ProcessPoolExecutor(max_workers=cpuCoreNumber) as executor:
        segment=int(len(proxyList)/cpuCoreNumber)
        for i in range(cpuCoreNumber-1):
            executor.submit(singleProcessEvokeMultiThreads,proxyList[segment*i:segment*(i+1)],q)
        executor.submit(singleProcessEvokeMultiThreads,proxyList[segment*(cpuCoreNumber-1):],q)
        executor.shutdown(wait=True)
    while not q.empty():
        validProxyList.append(q.get())
    print('从代理网站抓取到的有效代理数量：')

    #doublecheck
    doubleCheckedProxyList=[]
    print('doubleCheck有效代理数量：')
    return validProxyList

def singleProcessEvokeMultiThreads(proxyList,q):
    with thread.ThreadPoolExecutor(max_workers=5) as executor:
        result=executor.map(checkProxy,proxyList)
        for item in result:
            q.put(item)
        executor.shutdown(wait=True)

def checkProxy(proxy):
	print(proxy)
	httpbinurl='http://httpbin.org/ip'
	try:
		proxyHandler=request.ProxyHandler(proxy)
		opener=request.build_opener(proxyHandler)
		# opener.addheaders = headers
		request.install_opener(opener)
		html=request.urlopen(httpbinurl,timeout=10).read().decode('utf-8')
	except Exception as e:
		print(e)
	return html

#本模块使用proxyHandler测试代理，需要代理形式为{'protocal':'ip+:+port'}，
#本函数将[protocal,ip,port]整理为上述格式.
def arrangeProxyList(proxyList):
    arrangedList=[]
    for proxy in proxyList:
        arrangedList.append({proxy[0]:proxy[1]+':'+proxy[2]})
    return arrangedList

if __name__=='__main__':
    proxyList=[
        ['socks5','138.197.157.44','1080'],
        ['socks5','207.154.231.213','1080'],
        ['https','69.30.218.254','3128'],
    ]
    validList=filterValidProxiesMultiThreads(proxyList)
    for item in validList:
        print(item)