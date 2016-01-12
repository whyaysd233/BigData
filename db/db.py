"""The module is used to import data into the django database"""
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
import os
from datetime import datetime

# connect to the sqlite db
eng = create_engine('sqlite:///../caseView/db.sqlite3', encoding='utf8', convert_unicode=True)
metadata = MetaData(eng)

base = declarative_base()


class Case(base):
    """This class is the ORM of the database items of the django site"""
    __tablename__ = 'case_case'
    id = Column(String(10), primary_key=True)
    title = Column(String(20))
    time = Column(Date, nullable=True)
    court = Column(String(20), nullable=True)
    symbol = Column(String(20), nullable=True)
    content = Column(String, nullable=True)

    words = Column(String, nullable=True)

    isTarget = Column(Boolean, nullable=True, default=False)

    topic = Column(String(200), nullable=True)
    class1 = Column(String(30), nullable=True)
    class2 = Column(String(30), nullable=True)
    class3 = Column(String(30), nullable=True)


base.metadata.create_all(eng)
Session = sessionmaker(bind=eng)
session = Session(autocommit=True)


# session=Session()


def load_origin():
    """load original case data into db"""
    r = re.compile(r'<(.*),(.*),(.*),(.*)>\s*([\s\S]*)')
    base_dir = '/home/xsran/tmp/BigData/'
    for i in range(10):
        with session.begin(subtransactions=True):
            for key in os.listdir(base_dir + 'data_p_' + str(i)):
                fn = base_dir + 'data_p_' + str(i) + '/' + key

                with open(fn) as f:
                    line = f.read()
                    l = line.decode('utf8')
                    title, time, sym, court, content = r.findall(l[:200])[0]
                    content += l[200:]
                    try:
                        time = datetime.strptime(time, '%Y%m%d')
                    except Exception, e:
                        time = None

                    print i, key, title, time, sym, court
                    c = Case(id=key, title=title, time=time, symbol=sym, court=court, content=content)

                    session.add(c)


def load_pure():
    """load all unique words into db"""
    f = open('data_pure')
    with session.begin(subtransactions=True):
        for line in f:
            line = line.decode('utf8')
            k, w = line.split('\t', 1)
            c = session.query(Case).filter(Case.id == k).one()
            print k
            c.words = w


def load_classify():
    """ load the 3 dimensional tag """
    f = open('3-classes.txt')
    with session.begin(subtransactions=True):
        for line in f:
            line = line.decode('utf8')
            k = line.split('||')
            c = session.query(Case).filter(Case.id == k[0]).one()
            print k
            c.isTarget = True
            c.class1 = k[1]
            c.class2 = k[2]
            c.class3 = k[3]


def sub_n_br():
    r = re.compile(r'[\n\t]+')
    with session.begin(subtransactions=True):
        for c in session.query(Case).all():
            c.content = r.sub('<br>', c.content)
            print c.id


def sub_n_br2():
    r = re.compile(r'<(.*),(.*),(.*),(.*)>\s*([\s\S]*)')
    base_dir = '/home/xsran/tmp/BigData/'
    for i in range(10):
        with session.begin(subtransactions=True):
            for key in os.listdir(base_dir + 'data_p_' + str(i)):
                fn = base_dir + 'data_p_' + str(i) + '/' + key

                with open(fn) as f:
                    line = f.read()
                    l = line.decode('utf8')
                    title, time, sym, court, content = r.findall(l[:200])[0]
                    content += l[200:]
                    try:
                        time = datetime.strptime(time, '%Y%m%d')
                    except Exception, e:
                        time = None

                    print i, key, title, time, sym, court
                    c = session.query(Case).filter(Case.id == key).one()
                    c.content = content


def loadTopics():
    """ load case topic
    """
    with open('topics') as f:
        for line in f:
            line = line.decode('utf8')
            topics, ids = line.split('|')
            print topics
            with session.begin(subtransactions=True):
                for i in ids.split(' '):
                    i = i.strip()
                    print '>', i, len(i)
                    if len(i) == 0:
                        continue
                    c = session.query(Case).filter(Case.id == i).one()
                    c.topic = topics


if __name__ == '__main__':
    # load_origin()
    # load_pure()
    # load_classify()
    # sub_n_br()
    # sub_n_br2()
    loadTopics()
