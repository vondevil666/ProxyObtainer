"""
1.访问代理网站，获得html，筛出协议、ip、端口
2.协程测试ip有效性，测试目标网站http://www.httpbin.org/ip，当响应状态为200且从网站读取到的ip和代理ip相同，则ip有效。
3.有效ip存进本地validProxy.txt

4.运行本代码需要安装aiohttp模块，pip install aiohttp
"""

from urllib import request
from html.parser import HTMLParser
from datetime import datetime
import time
import random
import asyncio
import aiohttp
import os

httpbinUrl='http://www.httpbin.org/ip'       #用代理访问这个页面测试可用性，响应是json格式的请求者(代理)ip
headers = {
		'Pragma': 'no-cache',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
		'Cache-Control': 'no-cache',
		'Connection': 'close',
		'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 
							Chrome/56.0.2924.87 Safari/537.36'''
}

#HTMLParser，解析代理网站页面，筛出协议、ip、端口。html大体结构是一个table含多行信息，每行第2列是ip，第3列是端口，第6列是协议
class MyXiciParser(HTMLParser):
    enterTableRow=0     #标记进入含ip信息的一行，当离开该行时归零
    tdCounter=0         #遇到td则加一，遇到2、3、6行则将数据存入ipData
    resultList=[]       #存放整页多条ip、端口、协议的数据
    proxyData=[]        #存放一行的ip、端口、协议
    enterTag=0          #标记进入一个标签。HTMLParser会在starttag和endtag后分别调用handle_data()，有该标记只在starttag后调用handle_data()

    def handle_starttag(self,tag,attrs):
        self.enterTag=1
        if tag=='tr' and attrs:
            for (key,value) in attrs:
                if key=='class' and (value=='' or value=='odd'):
                    self.enterTableRow=1
        elif self.enterTableRow==1 and tag=='td':
            self.tdCounter+=1
        else:
            pass

    def handle_endtag(self,tag):
        self.enterTag=0
        if tag=='tr' and self.enterTableRow==1:
            self.enterTableRow=0
            self.tdCounter=0
            self.resultList.append(self.proxyData)
            self.proxyData=[]
        else:
            pass
    
    def handle_data(self,data):
        if self.enterTag!=1 or self.enterTableRow!=1 or self.tdCounter not in {2,3,6}:
            pass
        else:
            if self.tdCounter==2:
                self.proxyData.append(data.strip())
            elif self.tdCounter==3:
                self.proxyData.append(data.strip())
            elif self.tdCounter==6:
                self.proxyData.append(data.strip().lower())


#获得代理网站的html，验证代理使用协程，所以该访问网页不需复用
def getProxyWebHtml(proxyWebUrl):
    myRequest=request.Request(proxyWebUrl,headers=headers)
    with request.urlopen(myRequest) as f:
        if f.getcode()==200:
            return f.read().decode('utf-8')
    return None

#从本地取得html，防止测试中频繁访问网站导致拒绝访问
def getLocalWebHtml():
    path=os.path.dirname(__file__)+'\\'+'xiciLocalHtml.txt'
    with open(path,'r',encoding='utf-8') as f:
        return f.read()

#每次从代理网站取得html时睡眠随机时间，避免瞬间高频访问服务器
def sleepAwhile():
    sleepTime=random.uniform(3,6)
    print("抓取完成一个页面，睡眠%s秒"%sleepTime)
    time.sleep(sleepTime)

#获得西刺代理前三页的高匿ip、端口、协议
def getXiciProxies():
    proxyList=[]
    myParser=MyXiciParser()
    for xiciPage in range(1,2):
        html=getLocalWebHtml()        #测试时为了避免多次访问代理网站，所以从一个本地页面读取ip
        # html=getProxyWebHtml('http://www.xicidaili.com/nn/%s'%xiciPage)
        myParser.feed(html)
        proxyList.extend(myParser.resultList)
        myParser.resultList=[]        #一直使用同一个MyXiciParser对象，所以处理完一个页面后需要清空
        sleepAwhile()
    return proxyList

#将ip写入本地txt，格式为协议，ip，端口
def writeListToTxt(proxyList):    
    myFile=os.path.dirname(__file__)+'\\'+'validProxy.txt'
    with open(myFile,'w')as f:
        f.write(str(datetime.now())+'\n')   #文件第一行写入当前时间
        for data in proxyList:
            f.write(data+'\n')

#不同代理网站取得的ip原始数据格式不同，需要整理成为http://123.123.2.2:80的格式。aiohttp使用左侧格式的代理形式
def arrangeProxyForm(proxyList):
    arrangedProxyList=[]
    for rowNum in range(len(proxyList)):    #rowNum是包含协议、ip、端口的list，3个数据顺序可能不同
        proto=None;ip=None;port=None
        for data in proxyList[rowNum]:
            if data=='https':break          #aiohttp不支持https代理，所以不保存
            elif data=='http':proto=data    #当第一次为proto赋值后，进入后续循环后proto仍然保留赋值，也就是在新循环中没有新建proto变量，why？
            elif '.' in data:ip=data
            else:port=data
        try:proto and ip and port;arrangedProxyList.append(proto+'://'+ip+':'+port) #当三个变量都存在时才记录入表
        except:pass
    return arrangedProxyList

#拿到代理网站的proxy列表，用aiohttp协程访问httpbin.org/ip，返回有效的代理list，该函数是协程的入口
#使用协程三部曲：1.用tasks列表封装协程对象；2.在loop中运行tasks；3.从task.result()中取得结果（协程对象的返回值）
def filterValidProxies(proxyList):
    validProxyList=[]
    tasks=[]
    for proxy in proxyList:
        tasks.append(asyncio.ensure_future(getValidProxy(proxy)))
    loop=asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))
    for task in tasks:
        if task.result():validProxyList.append(task.result())
    print('从代理网站抓取到的有效代理数量：'+str(len(validProxyList)))

    #doublecheck
    tasks=[]
    for proxy in validProxyList:
        tasks.append(asyncio.ensure_future(doubleCheckValidProxy(proxy)))
    loop.run_until_complete(asyncio.gather(*tasks))
    validProxyList=[]
    for task in tasks:
        if task.result():validProxyList.append(task.result())
    print('doubleCheck有效代理数量：'+str(len(validProxyList)))
    loop.close()
    return validProxyList

#协程函数/协程对象。建立ClientSession时指定的connector的最大连接数好像没用。筛选出的代理没有区分代理种类（透明或匿名）
async def getValidProxy(proxy):
    try:
        async with aiohttp.ClientSession(headers=headers,connector=aiohttp.TCPConnector(limit=10)) as session:
            async with session.get(httpbinUrl,proxy=proxy,timeout=10) as response:
                ip=proxy[7:proxy.rindex(':')]
                html=await response.text()
                if response.status==200 and (ip in html):
                    return proxy
                else:return None
    except:
        # print('getValidProxy  error')
        pass

#对第一次选出的有效代理进行二次检查，访问MA，有效代理准备入库
#二次检查最好直接访问待爬取的网站
async def doubleCheckValidProxy(proxy):
    bandID=random.randint(0,200)
    doubleCheckUrl='http://www.metal-archives.com/bands/'+str(bandID)
    try:
        async with aiohttp.ClientSession(headers=headers,connector=aiohttp.TCPConnector(limit=10)) as session:
            async with session.get(httpbinUrl,proxy=proxy,timeout=10) as response:
                if response.status==200:return proxy
    except:
        pass

#程序入口。1.负责命令不同代理网站爬取proxy，2.整合后验证proxy有效性，3.最后将有效proxy写进本地txt文件
def main():
    proxyList=[]
    xiciProxyList=arrangeProxyForm(getXiciProxies())
    proxyList.extend(xiciProxyList)

    print('从代理网站抓取到代理数量：'+str(len(proxyList)))
    validProxyList=filterValidProxies(proxyList)
    for proxy in validProxyList:
        print(proxy)
    writeListToTxt(proxyList)
    print('finish')


main()