#coding:utf-8

import urllib.request
from urllib import error
import lxml.html
import re
import threading
import time
from MongoDB import MongoQueue
import multiprocessing

#download the html
def jd_downloader(url, retries):
    '''

    :param url: 爬取链接
    :param retries:容错次数
    :return:url对应的html
    '''

    user_agent = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19'
    header = {'User-Agent': user_agent}

    req = urllib.request.Request(url, headers=header)
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
    except error.URLError as e:
        html = None
        if hasattr(e, 'reason'):
            print('failed reached to a webserver')
            print(e.reason)
        if hasattr(e, 'code'):
            print('the error code is ', e.code)

        #retries
        if retries > 0 and 400 <= e.code < 500:
            jd_scrawler(url, retries-1)

    return html


#crawl info what we want
def jd_crawler(html):
    '''

    :param html:
    :return:    price:手机价格信息
                data_sku:拖动滚动条才能动态加载的下半页手机信息，每个商品对应一个ID
    '''

    if html is None:
        print('html is None')
        return
    try:
        tree = lxml.html.fromstring(html)
        #prices = tree.cssselect('div#J_goodsList > ul.gl-warp clearfix > li > div.gl-i-wrap > div.p-price > strong > i')
        prices = tree.cssselect('li.gl-item > div.gl-i-wrap > div.p-price > strong > i')   #
        data_sku = re.findall('<li class="gl-item" data-sku="(.*?)"', html)   #
    except:
        prices = None
        data_sku = None
        print('scrawler failed')

    return prices, data_sku

#通过遍历ID获取所有url
def get_links():
    links = []
    for i in range(1, 100, 2):
        links.append('https://search.jd.com/Search?keyword='+urllib.request.quote('手机')+'&enc=utf-8&wq='+urllib.request.quote('手机')+'&page={0}'.format(i))
        links.append('https://search.jd.com/Search?keyword='+urllib.request.quote('手机')+'&enc=utf-8&page={0}&scrolling=y&show_items='.format(i+1))
    return links

#
def handle_scrawl(url1, url2):
    global err
    try:
        err = 0

        #download url1
        h1 = jd_downloader(url1, 4)
        p_list1, data_sku1 = jd_crawler(h1)
        print('%s download completed'%(url1.split('&')[-1]))


        data = ''
        for i in range(len(data_sku1) - 1):
            data += data_sku1[i] + ','
        data += data_sku1[len(data_sku1) - 1]
        url2 += url2 + data

        #download url2
        h2 = jd_downloader(url2, 4)
        p_list2, data_sku2 = jd_crawler(h2)
        print('%s download completed'%(url2.split('&')[-3]))

        #for i in p_list1 + p_list2:
        #    print(i.text_content())
    except:
        err += 1
        if err > err_max:
            raise


def thread_link_crawler():
    '''

    :param thread_max_nums: 最多线程数量
    :param err_max:ID不连续的情况出现的最多次数
    :return:
    '''
    links = get_links()
    threads = []
    while threads or links:
        for thread in threads:
            if not thread.is_alive():
                # remove the stopped threads
                threads.remove(thread)
        while len(threads) < 10 and links:   #设置最大线程数为10
            url1 = links.pop(0)
            url2 = links.pop(0)
            thread = threading.Thread(target=handle_scrawl, args=(url1, url2))
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

#多进程爬取
def process_link_crawler(args):
    num_cpus = multiprocessing.cpu_count()
    print('starting {} processes'.format(num_cpus))
    processes = []
    for i in range(num_cpus):
        p = multiprocessing.Process(target=thread_link_crawler)
        p.start()
        processes.append(p)

    #wait for processes to complete
    for p in processes:
        p.join()


if __name__ == '__main__':

    links = get_links()
    err = 0    #避免因ID不连续出现的爬取错误
    threads = []

    start = time.time()

    process_link_crawler(args=None)

    end = time.time()
    print('it costs %.2f seconds'%(end-start))




