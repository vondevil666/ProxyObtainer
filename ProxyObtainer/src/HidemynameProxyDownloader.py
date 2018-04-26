
from html.parser import HTMLParser
import random
import time
from GetLocalHtml import getLocalWebHtml
from GetProxyWebHtml import getProxyWebHtml

#获得hidemyname代理前三页的高匿ip、端口、协议
def getHidemynameProxies():
    proxyList=[]
    myParser=MyHidemynameParser()
    for hidemynamePage in range(0,3):         #抓取1-3页
        # html=getLocalWebHtml('hidemynameLocalHtml.txt')        #测试时为了避免多次访问代理网站，所以从一个本地页面读取ip
        html=getProxyWebHtml('https://www.hidemyname.biz/proxy-list/?type=h&anon=234&start=%s#list'%(hidemynamePage*64))
        myParser.feed(html)
        proxyList.extend(myParser.resultList)
        myParser.resultList=[]        #一直使用同一个MyXiciParser对象，所以处理完一个页面后需要清空
        sleepAwhile('Hide my name代理')
    return proxyList

#每次从代理网站取得html时睡眠随机时间，避免瞬间高频访问服务器。proxySite参数是代理网站的名称，print()时方便辨识
def sleepAwhile(proxySite):
    sleepTime=random.uniform(3,6)
    print("抓取完成一个《%s》页面，睡眠%s秒"%(proxySite,sleepTime))
    time.sleep(sleepTime)

#HTMLParser，解析西刺代理网站页面，筛出协议、ip、端口。html大体结构是一个table含多行信息，每行第2列是ip，第3列是端口，第6列是协议
class MyHidemynameParser(HTMLParser):
    resultList=[]       #存放整页多条ip、端口、协议的数据
    proxyData=[]        #存放一行的ip、端口、协议
    enterIP=0
    enterPort=0

    def handle_starttag(self,tag,attrs):
        if tag=='td' and attrs:
            for (key,value) in attrs:
                if key=='class' and value=='tdl':
                    self.enterIP=1
        elif tag=='td' and self.enterIP==1:
            self.enterPort=1


    def handle_endtag(self,tag):
        pass
    
    def handle_data(self,data):
        if self.enterIP==1 and self.enterPort==0:
            self.proxyData.append(data)
        elif self.enterPort==1:
            self.proxyData.append(data)
            self.proxyData.append('http')
            self.resultList.append(self.proxyData)
            self.proxyData=[]
            self.enterIP=0
            self.enterPort=0

if __name__=='__main__':
    proxyList=getHidemynameProxies() #只能抓前三页
    for item in proxyList:
        print(item)
    print('done')