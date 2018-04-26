
from html.parser import HTMLParser
import random
import time
from GetLocalHtml import getLocalWebHtml
from GetProxyWebHtml import getProxyWebHtml

#获得西刺代理前三页的高匿ip、端口、协议
def getXiciProxies(start,end):
    proxyList=[]
    myParser=MyXiciParser()
    for xiciPage in range(start,end):         #抓取1-3页
        # html=getLocalWebHtml('xiciLocalHtml.txt')        #测试时为了避免多次访问代理网站，所以从一个本地页面读取ip
        html=getProxyWebHtml('http://www.xicidaili.com/nn/%s'%xiciPage)
        myParser.feed(html)
        proxyList.extend(myParser.resultList)
        myParser.resultList=[]        #一直使用同一个MyXiciParser对象，所以处理完一个页面后需要清空
        sleepAwhile('西刺代理')
    return proxyList

#每次从代理网站取得html时睡眠随机时间，避免瞬间高频访问服务器。proxySite参数是代理网站的名称，print()时方便辨识
def sleepAwhile(proxySite):
    sleepTime=random.uniform(3,6)
    print("抓取完成一个《%s》页面，睡眠%s秒"%(proxySite,sleepTime))
    time.sleep(sleepTime)

#HTMLParser，解析西刺代理网站页面，筛出协议、ip、端口。html大体结构是一个table含多行信息，每行第2列是ip，第3列是端口，第6列是协议
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

if __name__=='__main__':
    proxyList=getXiciProxies(1,3)
    for item in proxyList:
        print(item)
    print('done')