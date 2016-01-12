# coding=utf-8
import httplib2
import re
from pyquery import PyQuery as pq

hostname='example.com'

# 相关页面的http请求的header信息
hdstr3 = """Host: %s
Connection: keep-alive
Accept: */*
Origin: http://%s
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
DNT: 1
Referer: http://%s/Search/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4""" % (hostname,hostname,hostname)

hdstr = r"""Host: %s
Connection: keep-alive
Accept: */*
Origin: http://%s
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
DNT: 1
Referer: http://%s/search/keywords?Keywords=
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4""" % (hostname,hostname,hostname)

hdstr2 = r"""Host: %s
Connection: keep-alive
Cache-Control: max-age=0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36
DNT: 1
Referer: http://%s/search/keywords?Keywords=
Accept-Encoding: gzip, deflate, sdch
Accept-Language: zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4""" % (hostname,hostname)


class Spider(object):
    http = httplib2.Http(timeout=1)
    body = """IsLeaf=False&Keywords=&Cause=&LawFirm=&Lawyer=&AreaCode=&Court=&Judger=&ClassCodeKey=%s%%2C%s%%2C&IsGuide=False&SubKeywords=&Pager.PageIndex=%s&X-Requested-With=XMLHttpRequest"""
    r = re.compile(r"""<a target="_blank" href="/full/(\d*).html" class="title">""")
    hd = [i.strip().split(': ', 1) for i in hdstr.split('\n')]
    hd = dict(hd)

    def __init__(self, t, c):
        self.t = str(t)
        self.c = str(c)

    def get(self, i):
        """获得网页案件列表中一个页面内中的所有案件id

        每个列表页面包含10条案件，先获得该列表页面中的10个案件的id，
        然后依次请求这10个案例。列表页面可以直接指定第几页，但是案件的
        id只能先从列表页面获得。
        :param i:
        :return:
        """
        uri = "http://%s/Search/RecordSearch?FilterType=Keywords&IsAdv=False" % hostname
        body = self.body % (self.t, self.c, i,)
        hd = self.hd.copy()
        hd['Content-Length'] = str(len(body))
        a = self.http.request(uri, method='POST', headers=hd, body=body)
        return self.r.findall(a[1])

    @classmethod
    def getTotalNum(cls, t, c):
        """根据案件的文书性质和案由来获取满足条件的案例数量

        :param t:文书性质
        :param c:案由
        :return:案例的数量
        """
        hd = [i.strip().split(': ', 1) for i in hdstr.split('\n')]
        hd = dict(hd)
        # print '----------------'
        uri = 'http://%s/Search/ClassSearch?FilterType=Keywords&IsAdv=False' % hostname
        body = 'IsLeaf=False&Keywords=&Cause=&LawFirm=&Lawyer=&AreaCode=&Court=&Judger=&ClassCodeKey=%s%%2C%s%%2C&IsGuide=False&X-Requested-With=XMLHttpRequest'
        body = body % (t, c,)
        hd['Content-Length'] = str(len(body))
        a = cls.http.request(uri, method='POST', headers=hd, body=body)
        d = pq(a[1].decode('utf8'))
        s = d(' .active a').text()
        s = s.split(' ')[1]
        r = re.compile(r'\d+')
        s = r.findall(s)[0]
        return s

    def getDetails(self, i):
        """获得一个案件的具体内容

        :param i: 案件的id
        :return: 获取到的案件信息
        """
        hd = self.hd.copy()
        uri = "http://%s/full/%s.html" % (hostname,i,)
        a = self.http.request(uri, headers=hd)
        d = pq(a[1])
        title = d(".fullText h4").text()
        tc = d(".fullText .annexInfo span")
        if len(tc) == 2:
            time = tc[0].text
            sym = tc[1].text
        elif len(tc) == 1:
            if tc[0].text.isalnum():
                time = tc[0].text
                sym = ''
            else:
                time = ''
                sym = tc[0].text
        else:
            time = ''
            sym = ''
        court = d('.fullText .annexInfo a').text()

        text = d('.fullText .fullCon')
        c = text.contents()
        text = ''.join([i for i in c if isinstance(i, (str, unicode))])
        return (title, time, court, sym, text)

    @classmethod
    def getClassDetails(cls, t, c):
        """根据案件的文书性质和案由来获取目录信息以及不同类别下案件的数量

        :param t:文书性质
        :param c:案由
        :return:该类别的id，以及名称
        """
        hd = [i.strip().split(': ', 1) for i in hdstr3.split('\n')]
        hd = dict(hd)
        uri = 'http://%s/Search/ClassSearch?FilterType=Keywords&IsAdv=False' % hostname
        body = 'IsLeaf=False&Keywords=&Cause=&LawFirm=&Lawyer=&AreaCode=&Court=&Judger=&ClassCodeKey=%s%%2C%s%%2C&IsGuide=False&X-Requested-With=XMLHttpRequest'
        body = body % (t, c,)
        hd['Content-Length'] = str(len(body))
        a = cls.http.request(uri, method='POST', headers=hd, body=body)
        d = pq(a[1].decode('utf8'))
        pad = {3: '35', 5: '45', 7: '45'}
        pad = pad[len(c)]
        x = d('.classifyListMain:eq(1) .classifyList .paddingLeft%s a' % (pad,))
        l = [(i.attrib['cluster_code'], i.text_content().strip()) for i in x]
        l = zip(*l)

        pad = {3: '25', 5: '35', 7: '45'}
        pad = pad[len(c)]
        x = d('.classifyListMain:eq(1) .classifyList .paddingLeft%s a' % (pad,))
        t = (x[0].attrib['cluster_code'], x[0].text_content().strip())
        return ([t[0]] + list(l[0]), [t[1]] + list(l[1]))
