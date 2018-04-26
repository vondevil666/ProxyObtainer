import requests
def grab(proxy):
    try:
        print('proxy:::%s'%(proxy[0]+'://'+proxy[1]+':'+proxy[2]))
        r=requests.get('http://www.httpbin.org/ip',proxies={'http':proxy[0]+'://'+proxy[1]+':'+proxy[2]},timeout=5)
        print(r.text)
    except:pass

if __name__=='__main__':
    proxyList=[
            ['http','52.164.249.198','3128'],
            ['socks5','216.172.61.144','8080'],
            ['socks4','216.172.61.144','8080'],
        ]
    for proxy in proxyList:
        grab(proxy)