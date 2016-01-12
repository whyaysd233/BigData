# -*- coding: utf-8 -*-
import os
import os.path
import re

stopword = []
fin = open('stop')
for line in fin:
    stopword.append(line.strip().decode('utf8'))
fin.close()

rootdir = "D:\\lda\\origin"
fout = open('data', 'w')
for parent, dirnames, filenames in os.walk(rootdir):
    for filename in filenames:
        files = os.path.join(parent, filename)
        f = open(files)
        for line in f:
            line = line.strip()
            # index=re.findall(r"^.+?(\d+),<",line)[0]
            index = f.name.split('\\')[-1].split('.')[0]
            content = line.split('>', 1)[1].decode('utf8').split()
            out = ""
            for item in content:
                #				item=item.decode('utf8')
                if len(item) < 2 or not re.match(
                        ur".*[\u96f6\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343\u4e07\u67d0\u5143\u5e74\u6708\u65e5\u7701\u5e02\u53bf]+.*",
                        item) == None:
                    continue
                if not re.match(ur"[\u4e00-\u9fa5]+", item) == None:
                    if not item in stopword:
                        out = out + item + " "
            fout.write(index + '\t' + out.encode('utf8') + '\n')
        f.close()
fout.close()
