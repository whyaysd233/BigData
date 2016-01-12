"""Spliting the case into words"""
import jieba
import os
import re
import sys

d = '/home/xsran/tmp/BigData/'


def main():
    r = re.compile('\s+')
    ct = 0
    for i in sys.argv[1:]:
        i = str(i)

        # use this dir to store the splited data
        if not os.path.exists(d + 'data_c_' + i):
            os.mkdir(d + 'data_c_' + i)

        # split case
        for fn in os.listdir(d + 'data_p_' + i):
            with open(d + 'data_p_' + i + '/' + fn) as f:
                doc = f.read()
            doc = jieba.cut(doc)
            doc = ' '.join(doc)
            # replace blank characters with space
            doc = r.sub(' ', doc)
            with open(d + 'data_c_' + i + '/' + fn, 'w') as f:
                f.write(doc.encode('utf8'))
            ct += 1
            print fn, ct


if __name__ == '__main__':
    main()
