""" Extracting case test from the html

There are many html tags in the original web pages.
This file is aimed at extracting the useful case data from the web pages.
"""
from scrapy.selector import Selector
import sys
import os
import re
import jieba

d = '/home/xsran/tmp/BigData/data'


def parse(doc):
    s = Selector(text=doc)

    title = s.css(".fullText h4::text").extract()
    title = title[0] if len(title) == 1 else ''
    tmp = s.css(".fullText .annexInfo span::text").extract()
    rd = re.compile('\d+')
    if len(tmp) == 2:
        time, symble = tmp
    elif len(tmp) == 1:
        if rd.match(tmp[0]):
            time = tmp[0]
            symble = '--'
        else:
            time = '--'
            symble = tmp[0]
    else:
        time, symble = '--', '--'
    court = s.css(".fullText .annexInfo a::text").extract()
    court = court[0] if len(court) == 1 else ''
    content = ''.join(s.css(".fullText .fullCon::text").extract())
    return '<%s,%s,%s,%s>\n\n%s' % (
        title.encode('utf8'),
        time.encode('utf8'),
        symble.encode('utf8'),
        court.encode('utf8'),
        content.encode('utf8'))


def main():
    args = sys.argv[1:]
    reobj = re.compile('\s+')
    ct = 0
    print args
    for a in args:
        files = os.listdir(d + str(a))
        # print files[:10]
        if not os.path.exists(d + '_p_' + a):
            os.mkdir(d + '_p_' + a)
        if not os.path.exists(d + '_c_' + a):
            os.mkdir(d + '_c_' + a)
        for fn in files:
            with open(d + a + '/' + fn) as f:
                doc = f.read()
                r = parse(doc)
            with open(d + '_p_' + a + '/' + fn, 'w') as f:
                f.write(r)
            doc = jieba.cut(r)
            doc = ' '.join(doc)
            doc = reobj.sub(' ', doc)
            with open(d + '_c_' + a + '/' + fn, 'w') as f:
                f.write(doc.encode('utf8'))
            ct += 1
            print fn, ct


if __name__ == '__main__':
    main()
