#coding:utf-8

import urllib.request
from urllib import error
import lxml.html
import re

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

if __name__ == '__main__':

    links = get_links()
    err = 0
    while(links and err < 5):
        url1 = links.pop()
        url2 = links.pop()
        #避免因ID不连续出现的爬取错误
        try:
            h1 = jd_downloader(url1, 4)

            p_list1, data_sku1 = jd_crawler(h1)

            data = ''
            for i in range(len(data_sku1)-1):
                data += data_sku1[i] + ','
            data += data_sku1[len(data_sku1)-1]
            url2 += url2+data

            h2 = jd_downloader(url2, 4)
            p_list2, data_sku2 = jd_crawler(h2)
            for i in p_list1+p_list2:
                print(i.text_content())
        except:
            err += 1