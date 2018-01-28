#coding:utf-8

from urllib.request import Request, urlopen
'''
def downloader(url):
    user_agent = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19'
    headers = {'User-agent':user_agent}
    req = Request(url, headers = headers)
    try:
        html = urlopen(url).read()
    except error.URLError as e:
        if hasattr(e, 'reason'):
            print('we failed reach to a webserver')
            print(e.reason)
        if hasattr(e, 'code'):
            print('the server could not fullfill the request')
            print(e.code)
    return html
'''

from urllib import error
from requests import request

def downloader(url):
    user_agent = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19'
    headers = {'User-agent':user_agent}
    req = request('Get', url, headers = headers)
    try:
        html = req.text
    except error.URLError as e:
        if hasattr(e, 'reason'):
            print('we failed reach to a webserver')
            print(e.reason)
        if hasattr(e, 'code'):
            print('the server could not fullfill the request')
            print(e.code)
    return html

if __name__ == '__main__':

    #results of search mobilephone in tianmao
    url = 'https://list.tmall.com/search_product.htm?q=%CA%D6%BB%FA&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton'
    print(downloader(url))



