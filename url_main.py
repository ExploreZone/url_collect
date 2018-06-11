#coding=utf-8

import requests
import sys
import Queue
import threading
from bs4 import BeautifulSoup as bs
import time
import urlparse

urls_get = []
#定义域名组
domains=[]
# urls = []
#单页面收集url线程
class craw_onepage(threading.Thread):
    def __init__(self,queue,name):
        threading.Thread.__init__(self)
        self.urls = queue
        self.name =name
    def run(self):
        print "[ * ]"+self.name+"start work："

        header = {'Accept-Encoding': 'gzip, deflate, br',
                'Cookie': 'bid=LrQN31nGWQQ; ll="118099"; __utmc=30149280; __utmz=30149280.1516180100.4.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _vwo_uuid_v2=87044A8644A6B35F343DEF23592CF1D2|a45ff09f0866b72a0db3c7e82de8d829; ap=1; ct=y; __utma=30149280.1648116166.1513566116.1516180100.1516194462.5; ps=y; __utmb=30149280.3.10.1516194462; dbcl2="154698815:25XxaBZL8xU"; ck=DM63; push_noty_num=0; push_doumail_num=0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36}'}
        while True:
            global queueLock
            queueLock.acquire()
            if not self.urls.empty():
                url= self.urls.get()
                queueLock.release()
                print "[ * ] "+self.name+":--->"+url
                print "[ * ] get success"
            else:
                queueLock.release()
                exit(0)
            time.sleep(0.05)
            try:
                req = requests.get(url=url,headers=header,timeout=2)
                page_content = req.content
                soup = bs(page_content,"lxml")
                urls = soup.find_all("a","c-showurl")
                for url in urls:
                    # url_file.write(url)
                    global url_num,domains
                    url_num = url_num + 1
                    code_url =  url["href"]
                    # 保证url可以被访问，2s延时
                    req_code = requests.get(code_url,headers=header,timeout=2)
                    url_decode = req_code.url
                    # 对数据进行清理，去重
                    if "=" in url_decode:
                        domain = urlparse.urlparse(url_decode)[1]
                        if domain not in domains:
                            domains.append(domain)
                            url_file.write(url_decode+"\n")
                            # 最终的数据
                            urls_get.append(url_decode)
                            url_num = url_num + 1
                            time.sleep(0.05)
            except Exception as e:
                print e
class init_parameter():
    def __init__(self,threads_num,queue,keyword,pages,threads):
        self.threads_num=int(threads_num)
        self.queue = queue
        self.keyword = keyword
        self.pages = int(pages)
        self.threads = threads
        self.threads = threads
    def init_thread(self):
        print "[ * ] start to create threading:"
        for i in range(self.threads_num):
            create_thread = craw_onepage(self.queue,"thread %d " %i)
            self.threads.append(create_thread)
            print "create threading %d success" %i
    def init_queue(self):
        print "[ * ] start create queue:"
        for i in range(self.pages):
            i=i*10
            url = "https://www.baidu.com/s?wd="+self.keyword+"&pn="+str(i)
            self.queue.put(url)
            print "[ * ] create queue %d success!" %i
def main():
    # 有一个不错的参数输入方法：a=int(raw_input("enter number:"))
    global queueLock
    queueLock = threading.Lock()
    time_start = time.asctime()
    print "[ * ] welcome to my urlgeting tools!"
    if len(sys.argv)<4:
        print "[ * ] usage: python url_main.py keyword pages thread_num"
        exit(0)
    global aurl_num
    global url_file
    url_file = open("url.txt", "a+")
    url_num = 0
    keyword = sys.argv[1]
    pages = sys.argv[2]
    threads_num = sys.argv[3]
    threads = []
    queues = Queue.Queue()
    paremeter = init_parameter(threads_num, queues, keyword, pages, threads)
    queue_paremeter = paremeter.init_queue()
    thread_paremeter = paremeter.init_thread()
    for thread_i in threads:
        thread_i.start()
    for thread_i in threads:
        thread_i.join()

    # queues.join()
    print "[ * ] ok"
    print url_num
    time_end = time.asctime()
    print time_start
    print time_end
    url_file.write("[ * ] 一共有 %d 条数据"%url_num)

    # print "using time: "+str(time_use)
    exit(0)


if __name__ == '__main__':
    main()
