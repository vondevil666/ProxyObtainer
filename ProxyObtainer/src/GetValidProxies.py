"""
本工具抓取不同代理网站的代理，对代理进行两次验证，最后将有效代理写入本地的validProxy.txt

使用：
1.运行本代码需要安装aiohttp模块，pip install aiohttp
2.双击.py文件或者用ide编译执行

工具工作流程：
1.访问代理网站，获得html，筛出协议、ip、端口
2.用协程测试ip有效性，测试目标网站http://www.httpbin.org/ip，当响应状态为200且从网站读取到的ip和代理ip相同，则ip有效。
3.对真实需要抓取的网站进行二次验证，需要在doubleCheckReturnValidProxy()函数中指定访问地址
4.有效ip存进本地validProxy.txt

"""
# from FilterValidProxies import filterValidProxies
from FilterValidProxiesMultiThreads import filterValidProxiesMultiThreads
from writeListToSQLite import writeListToSQLite
from XiciProxyDownloader import getXiciProxies
from ProxydbProxyDownloader import getProxydbProxies
from HidemynameProxyDownloader import getHidemynameProxies

from datetime import datetime
import asyncio
import aiohttp
import os
import re

httpbinUrl='http://www.httpbin.org/ip'       #用代理访问这个页面测试可用性，响应是json格式的请求者(代理)ip

#将筛选过的有效代理写入本地txt，格式为协议，ip，端口，如：http://221.229.18.158:808
def writeListToTxt(proxyList):    
    myFile=os.path.dirname(os.path.dirname(__file__))+'\\'+'validProxy.txt'
    with open(myFile,'w')as f:
        f.write(str(datetime.now())+'\n')   #文件第一行写入当前时间
        for data in proxyList:
            f.write(data+'\n')

#不同代理网站取得的ip原始数据格式不同，需要整理成为http://123.123.2.2:80的格式。aiohttp使用左侧格式的代理形式，并且不接受https代理
# def arrangeProxyForm(proxyList):
#     arrangedProxyList=[]
#     for rowNum in range(len(proxyList)):    #rowNum是包含协议、ip、端口的list，3个数据顺序可能不同
#         proto=None;ip=None;port=None
#         for data in proxyList[rowNum]:
#             if data=='https':break          #aiohttp不支持https代理，所以不保存
#             elif data=='http':proto=data    #当第一次为proto赋值后，进入后续循环后proto仍然保留赋值，也就是在新循环中没有新建proto变量，why？
#             elif '.' in data:ip=data
#             else:port=data
#         try:proto and ip and port;arrangedProxyList.append(proto+'://'+ip+':'+port) #当三个变量都存在时才记录入表
#         except:pass
#     return arrangedProxyList

#替换上面一个函数，本函数将代理整理成[[protocal,ip,port],[protocal,ip,port],[]....]的形式。每个元素中的3个子元素有顺序。
def arrangeProxyForm(proxyList):
    arrangedProxyList=[]
    for rowNum in range(len(proxyList)):    #rowNum是包含协议、ip、端口的list，3个数据顺序可能不同
        proto=None;ip=None;port=None
        for data in proxyList[rowNum]:
            if '.' in data:ip=data
            elif re.search('[a-z]',data):proto=data
            else:port=data
        try:proto and ip and port;arrangedProxyList.append([proto,ip,port]) #当三个变量都存在时才记录入表
        except:pass
    return arrangedProxyList


#程序入口。1.负责命令不同代理网站爬取proxy，2.整合不同网站抓取的代理，验证proxy有效性，3.最后将有效proxy写进本地txt文件
def main():
    proxyList=[]
    # xiciProxyList=arrangeProxyForm(getXiciProxies(1,2))   #每页100个，每天大概更新3页
    # proxyList.extend(xiciProxyList)
    # proxydbProxyList=arrangeProxyForm(getProxydbProxies(1,11))   #每页15个，不提供几小时内更新的结果，但24小时内更新的非常多
    # proxyList.extend(proxydbProxyList)
    hidemynameProxyList=arrangeProxyForm(getHidemynameProxies())
    proxyList.extend(hidemynameProxyList)
    print('从代理网站抓取到代理数量：'+str(len(proxyList)))

    # validProxyList=filterValidProxies(proxyList)
    validProxyList=filterValidProxiesMultiThreads(proxyList)
    for proxy in validProxyList:
        print(proxy)
    # writeListToTxt(proxyList)   #现在写入的是抓取到但未经过验证的代理，因为验证之后就几乎没有有效代理了。。。
    db=os.path.dirname(os.path.dirname(__file__))+r'\proxyList.db'
    writeListToSQLite(validProxyList,db)    #代理写入数据库，数据库是文件夹下的proxyList.db
    print('finish')

if __name__=='__main__':
    main()