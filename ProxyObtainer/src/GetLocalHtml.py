
import os

#从本地取得html，防止测试中频繁访问网站导致拒绝访问
def getLocalWebHtml(fileName):
    path=os.path.dirname(os.path.dirname(__file__))+'\\'+fileName
    with open(path,'r',encoding='utf-8') as f:
        return f.read()

if __name__=='__main__':
    print(getLocalWebHtml())