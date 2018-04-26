#该模块是使用协程访问并发访问网络的模板，三个小模块全都包括

import aiohttp
import asyncio
import random
import os

headers = {
		'Pragma': 'no-cache',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
		'Cache-Control': 'no-cache',
		'Connection': 'close',
		'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 
							Chrome/56.0.2924.87 Safari/537.36''',
	}
proxyList=[]

def getRandomProxy():
	return proxyList[random.randint(0,len(proxyList)-1)]

async def corotineModel(semaphore,session,proxy,url,id):
	try:
		async with semaphore:
			async with session.get(url,proxy=proxy,timeout=20) as response:
				html=await response.text()
				print(proxy)
				if response.status==200:
					return [id,html]
				else:return None
	except:
		pass

#新增传递id参数，在协程对象的返回值中包含访问页面的id，从task.result()可知哪些访问成功，哪些不成功
async def tasksModel(start,end):
	tasks=[]
	result=[]
	baseUrl='http://www.metal-archives.com/bands//1'
	semaphore=asyncio.Semaphore(100)
	connector=aiohttp.TCPConnector(limit=100)
	async with aiohttp.ClientSession(headers=headers,connector=connector) as session:
		for id in range(start,end):
			tasks.append(asyncio.ensure_future(corotineModel(semaphore,session,getRandomProxy(),baseUrl,id)))
		await asyncio.gather(*tasks)
	for task in tasks:
		if task.result():
			result.append(task.result())
	connector.close()
	return result

def loopModel():
	localProxyFile=os.path.dirname(__file__)+'\\'+'长效代理.txt'
	with open(localProxyFile,'r') as f:
		proxyList.extend(f.read().splitlines()[1:])
	loop=asyncio.get_event_loop()
	result=loop.run_until_complete(tasksModel(1,10))
	print("使用代理成功访问%s个页面"%len(result))
	for r in result:
		pass
		# print(str(r))
	loop.close()

loopModel()	#start