
from html.parser import HTMLParser
import random
import time
import re
import base64
from GetLocalHtml import getLocalWebHtml
from GetProxyWebHtml import getProxyWebHtml

#获得西刺代理前三页的高匿ip、端口、协议
def getProxydbProxies(start,end):
    proxyList=[]
    myParser=MyProxydbParser()
    for proxydbPage in range(start-1,end-1):         #抓取1-3页
        # html=getLocalWebHtml('proxydbLocalHtml.txt')        #测试时为了避免多次访问代理网站，所以从一个本地页面读取ip
        url='http://proxydb.net/?protocol=http&anonlvl=2&anonlvl=3&anonlvl=4&country=&offset=%s'%(proxydbPage*15)
        html=getProxyWebHtml(url)
        myParser.feed(html)
        proxyList.extend(myParser.resultList)
        myParser.resultList=[]        #一直使用同一个Parser对象，所以处理完一个页面后需要清空
        sleepAwhile('proxydb代理')
    return proxyList

#每次从代理网站取得html时睡眠随机时间，避免瞬间高频访问服务器。proxySite参数是代理网站的名称，print()时方便辨识
def sleepAwhile(proxySite):
    sleepTime=random.uniform(2,4)
    print("抓取完成一个《%s》页面，睡眠%s秒"%(proxySite,sleepTime))
    time.sleep(sleepTime)

#HTMLParser，解析西刺代理网站页面，筛出协议、ip、端口。html大体结构是一个table含多行信息，每行第2列是ip，第3列是端口，第6列是协议
class MyProxydbParser(HTMLParser):
    resultList=[]       #存放整页多条ip、端口、协议的数据
    enterScript=0          #标记进入一个标签。HTMLParser会在starttag和endtag后分别调用handle_data()，有该标记只在starttag后调用handle_data()
    tbodyTag=0          #没进入tbody前什么都不做

    def handle_starttag(self,tag,attrs):
        if tag=='tbody' and self.tbodyTag==0:self.tbodyTag=1
        elif tag=='script' and self.tbodyTag==1:
            self.enterScript=1
        else:pass

    def handle_endtag(self,tag):
        if tag=='tbody' and self.tbodyTag==1:self.tbodyTag=0
        else:pass
    
    def handle_data(self,data):
        if self.enterScript!=1:pass
        else:
            self.resultList.append(getProxy(data))
            self.enterScript=0


'''
该函数用来从代理网站proxydb.net每行含代理信息的html文本中提取出代理ip和端口，协议全部为http。
proxydb.net家的html结构，每行代理信息中的ip都被简单隐藏，ip被拆成前后两部分，前一部分就是真实ip的逆字符串；
后一部分由base64编码，需解码才能拿到真实信息；端口信息由一个加减法得出，用eval()即可算出端口
'''
def getProxy(html):
    firstReversedIpHavles=""        #真实ip前一部分
    secondIpHavles=""
    html=html.replace('\'','\"')    #将单引号替换成双引号，否则用正则过程中比较麻烦

    #得到ip前一部分
    a=re.search('([0-9\.]*)\"\.split',html)
    if a:firstReversedIpHavles=a.group(1)[::-1]
    else:
        print("First Reversed Ip Havles Not Found")
        return None
    # print('firstReversedIpHavles:'+firstReversedIpHavles)
    
    #得到ip后半段，先用正则抓出为类似'\x4c\x6a'的字符串原文，必须去掉\x后再用bytes.fromhex()转成16进制，塞给b64decode，
    #用b64decode解码得到'b'07.45''这种字符串，再用切片得到07.45即ip后半段
    b=re.search('atob\(\"([\s\S]*)\"\.replace',html)
    if b:
        secondIpHavles=b.group(1).replace(r'\x','')
        secondIpHavles=bytes.fromhex(secondIpHavles)    #类型为bytes
        secondIpHavles=base64.urlsafe_b64decode(secondIpHavles)
        secondIpHavles=str(secondIpHavles)[2:-1]
    else:
        print("Second Ip Havles Not Found")
        return None
    # print('secondIpHavles:'+secondIpHavles)

    #得到端口号，用正则抓出加减法字符串，再用eval()即可得到加减法结果
    c=re.search('var pp = ([-+0-9 ]*)-1;',html)
    if c:port=eval(c.group(1))
    else:
        print("Port Not Found")
        return None
    # print('port:'+str(port))

    return 'http',str(firstReversedIpHavles)+str(secondIpHavles),str(port) #将端口号、IP、协议名用list返回

if __name__=='__main__':
    proxyList=getProxydbProxies(1,4)
    for item in proxyList:
        print(item)
    print('done')