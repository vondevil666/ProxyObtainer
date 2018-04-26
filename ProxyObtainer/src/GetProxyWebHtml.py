'''
下载代理网站页面模块，有默认headers，可以修改或追加headers属性，可以指定不同网站使用不同编码
'''

from urllib import request

headers = {
        'Accpet':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Pragma':'no-cache',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
		'Cache-Control': 'no-cache',
		'Connection': 'close',
		'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 
							Chrome/56.0.2924.87 Safari/537.36'''
}

#获得代理网站的html
def getProxyWebHtml(proxyWebUrl):
    complementHeaders(proxyWebUrl)     #针对每个网站添加不同的headers信息
    myRequest=request.Request(proxyWebUrl,headers=headers)
    with request.urlopen(myRequest) as f:
        if f.getcode()==200:
            return f.read().decode(getEncoding(proxyWebUrl))
    return None

#某些网站使用编码不是utf-8，例如hidemyname需要从毛子网站才能采集，编码为windows-1251
def getEncoding(proxyWebUrl):
    if 'hidemyname' in proxyWebUrl:
        return 'windows-1251'
    else:
        return 'utf-8'

#修改或追加headers
def complementHeaders(proxyWebUrl):
    if 'hidemy.name' in proxyWebUrl:
        headers['Accept-Encoding']='gzip, deflate, br'  #发现：请求中使用不同编码，返回值可能会有问题
        headers['Host']='hidemy.name'
        headers['Referer']='https://www.hidemyname.biz/proxy-list/ip/'
        headers['Upgrade-Insecure-Requests']='1'

if __name__=='__main__':
    html=getProxyWebHtml('https://www.hidemyname.biz/proxy-list/?type=h&anon=234&start=0#list') #hidemyname
    # html=getProxyWebHtml('http://proxydb.net/?protocol=http&anonlvl=2&anonlvl=3&anonlvl=4&country=&offset=0') #proxydb
    print(html)