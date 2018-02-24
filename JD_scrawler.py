#coding:utf-8

import urllib.request
import json
from urllib import error
import lxml.html
from selenium import webdriver
import time
import http.cookiejar
import re



head = {
    'Host': 'search.jd.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&suggest=1.def.0.V07&wq=shouji&pvid=24767468eb52455a91e91ae3e0ec08cf',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': '__jda=122270672.15153254211052084628628.1515325421.1517922832.1518005706.16; unpl=V2_ZzNtbUNTQUJyDEVdfkpaDGIHFglLUEdAcw9OVC8fXVI3ABNeclRCFXwUR1dnGFsUZwsZWERcRh1FCHZUehhdBGYBFV5GZxpFKwhFVidSbDVkAyJVcldHFXEKRVB%2bGlwFZgcRXEtSRBZ8D0VdSylbNVczE21DZ0IlPmZHGXsdXAFlABZYQVdDFHELR11%2bHl8MYAAbbUNnQA%3d%3d; __jdv=122270672|www.hao123.com|t_1000003625_hao123mz|tuiguang|053f65284b78455e865d7691e70fa202|1517917670088; __jdu=15153254211052084628628; 3AB9D23F7A4B3C9B=CKVTAVRNGLVFI5CXHKEBJBH7KDN5742YDWWMSNK3BJLIUSIAWAS2GQXHS4IF2J64C2MVPODN3NVE2CCIXCOTQSH4PI; user-key=98f1ccaf-1100-479b-871c-7d71a8384a3c; cn=0; xtest=9871.cf6b6759; ipLoc-djd=1-72-2799-0; qrsc=3; __jdb=122270672.2.15153254211052084628628|16.1518005706; __jdc=122270672; PCSYCityID=1930; rkv=V0700',
    'Connection': 'keep-alive'
}

def makeOpener(head):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener

def getHtml(url):
    oper = makeOpener(head)
    if oper is not None:
        page = oper.open(url).read().decode()
    return page

#download the html

def jd_downloader(url, retries):

    user_agent = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19'
    header = {'User-Agent': user_agent}
    if None:
        driver = webdriver.Firefox()  # 执行该操作之后会打开一个空的Firefox页面
        driver.get(url)  #
        js = 'var q=document.documentElement.scrollTop=10000'
        driver.execute_script(js)
        time.sleep(5)

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


#crawl the info we want

def jd_crawler(html):

    if html is None:
        print('html is None')
        return
    try:
        tree = lxml.html.fromstring(html)
        #prices = tree.cssselect('div#J_goodsList > ul.gl-warp clearfix > li > div.gl-i-wrap > div.p-price > strong > i')
        prices = tree.cssselect('li.gl-item > div.gl-i-wrap > div.p-price > strong > i')
        data_sku = re.findall('<li class="gl-item" data-sku="(.*?)"', html)
    except:
        prices = None
        data_sku = None
        print('scrawler failed')

    return prices, data_sku


if __name__ == '__main__':

    url1 = 'https://search.jd.com/Search?keyword='+urllib.request.quote('手机')+'&enc=utf-8&pvid=5105323693044a27b7aef5856a407382'
    url2 = 'https://search.jd.com/Search?keyword='+urllib.request.quote('手机')+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&page=2&s=29&scrolling=y&log_id=1517920176.84671&tpl=3_M&show_items='

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

