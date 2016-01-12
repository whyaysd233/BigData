# coding=utf-8
import sys, os
from PyQt4 import QtGui, QtCore, uic
import time
import claw
import random

# 文书性质信息
typeName = [u'判决书', u'裁定书', u'决定书', u'调解书', u'其它文书']
typeId = ['001', '002', '003', '004', '005']

# 一级目录信息
className = [u'请选择', u'刑事', u'民事', u'知识产权', u'行政', u'执行', u'国家赔偿']
classId = [None, '001', '002', '003', '004', '005', '006', '007']


class WorkThread(QtCore.QThread):
    """后台程序，用于在后台进程爬取数据

    该类用于执行后台爬取数据的进程，使界面和爬取数据的执行在两个进程中，
    防止界面卡死
    """
    updated = QtCore.pyqtSignal(int)

    def __init__(self, typeId, classId, t, num, path='./data/'):
        QtCore.QThread.__init__(self)
        self.spider = claw.Spider(typeId, classId)
        self.t = t
        self.num = num
        self.cur = 0
        self.path = path
        if not os.path.exists(path):
            os.mkdir(path)

    def __del__(self):
        self.wait()

    def save(self, data, id):
        """保存一份法律文书

        :param data: 文书数据
        :param id: 文书id
        :return: 无
        """
        self.cur += 1
        i = self.cur / 1000
        d = 'part-' + str(i).zfill(5) + '/'

        d = os.path.join(self.path, d)
        if not os.path.exists(d):
            os.mkdir(d)
        with open(d + id + '.txt', 'w') as f:
            data = '%s||%s||%s||%s\n\n%s' % data
            f.write(data.encode('utf8'))

    def run(self):
        """在后台运行爬虫，不断的获取数据
        """
        num = 0
        # 每个列表中10个案例，可以直接指定打开第几页列表
        for i in range(self.num / 10):
            # 从列表页面获得这10个案件的id，在依次获得这10个案例的内容
            all = self.spider.get(i)
            print 'all', all
            for n in all:
                data = self.spider.getDetails(n)
                self.save(data, n)
                num += 1
                self.updated.emit(num)
                time.sleep(random.random() * self.t)
            time.sleep(random.random() * self.t)
            self.emit(QtCore.SIGNAL('update(QString)'), "from work thread " + str(i))
        self.terminate()


class Window(QtGui.QWidget):
    """使用PyQt制作的爬虫界面，经过打包后的程序位于dist文件夹下。

    可以在windows下直接运行。
    （可能需要安装微软的运行时库）
    """

    def __init__(self):
        super(Window, self).__init__()
        self.ui = uic.loadUi('ui.ui', self)
        self.typeId = typeId[0]
        self.classId = classId[0]
        self.totalNum = 0
        self.started = False

        self.connect(self.ui.buttonStart, QtCore.SIGNAL('clicked()'), self.start)
        for n in typeName:
            self.ui.comboType.addItem(n)
        for n in className:
            self.ui.comboClass.addItem(n)

        self.class2 = []
        self.class3 = []
        self.sleep = 0.1

        self.ui.progress.setValue(0)

        self.connect(self.ui.comboClass, QtCore.SIGNAL('activated (int)'), self.comboClssClicked)
        self.connect(self.ui.comboClass2, QtCore.SIGNAL('activated (int)'), self.comboClss2Clicked)
        self.connect(self.ui.comboClass3, QtCore.SIGNAL('activated (int)'), self.comboClss3Clicked)
        self.connect(self.ui.comboType, QtCore.SIGNAL('activated (int)'), self.comboTypeClicked)
        self.connect(self.ui.sliderPageTime, QtCore.SIGNAL('valueChanged(int)'), self.sliderPageTimeUpdate)
        self.ui.labelSave.setText(os.getcwd())
        self.path = os.getcwd()
        print self.path
        self.connect(self.ui.buttonSave, QtCore.SIGNAL('clicked()'), self.setDir)
        self.setWindowTitle(u'万能蜘蛛')

    def start(self):
        if not self.classId:
            return
        if self.started:
            self.started = False
            self.ui.conf.setEnabled(True)
            self.workThread.terminate()
            self.ui.buttonStart.setText('Start')
        else:
            print 'Start'
            n = claw.Spider.getTotalNum(self.typeId, self.classId)
            self.totalNum = int(n)
            self.started = True
            self.ui.conf.setEnabled(False)
            self.ui.progress.setRange(0, self.totalNum)
            self.ui.progress.setValue(0)
            self.ui.buttonStart.setText('Stop')
            # QtGui.qApp.processEvents()
            t = self.ui.sliderPageTime.value()
            self.workThread = WorkThread(self.typeId, self.classId, self.sleep, self.totalNum)
            self.workThread.updated.connect(self.update)
            self.workThread.start()

    def comboClssClicked(self, i):
        """一级目录回调程序

        每次更改一级目录中选择的项目后，都会从网络获得二级目录列表，
        以及每个目录下的法律文书数量"""
        self.classId = classId[i]
        print i, self.classId
        # n = claw.Spider.getTotalNum(self.typeId,self.classId)
        # self.totalNum=int(n)
        if self.classId:
            ids, items = claw.Spider.getClassDetails(self.typeId, self.classId)
            self.ui.comboClass2.clear()
            for i in items:
                self.ui.comboClass2.addItem(i)
            self.ui.comboClass3.clear()
            self.class2 = ids
        else:
            self.ui.comboClass2.clear()
            self.ui.comboClass3.clear()

    def comboClss2Clicked(self, i):
        """二级目录回调程序

        每次更改二级目录中选择的项目后，都会从网络获得三级目录列表，
        以及每个目录下的法律文书数量"""
        self.classId = self.class2[i]
        print i, self.classId
        # n = claw.Spider.getTotalNum(self.typeId,self.classId)
        # self.totalNum=int(n)

        ids, items = claw.Spider.getClassDetails(self.typeId, self.classId)
        self.ui.comboClass3.clear()
        for i in items:
            self.ui.comboClass3.addItem(i)
        self.class3 = ids

    def comboClss3Clicked(self, i):
        """三级目录回调程序"""
        self.classId = self.class3[i]
        print i, self.classId
        # n = claw.Spider.getTotalNum(self.typeId,self.classId)
        # self.totalNum=int(n)
        ids, items = claw.Spider.getClassDetails(self.typeId, self.classId)

    def comboTypeClicked(self, i):
        """文书性质列表回调程序"""
        self.typeId = typeId[i]
        print i, self.typeId
        if self.classId:
            ids, items = claw.Spider.getClassDetails(self.typeId, self.classId)
            self.ui.comboClass2.clear()
            for i in items:
                self.ui.comboClass2.addItem(i)
            self.ui.comboClass3.clear()
            self.class2 = ids
        else:
            self.ui.comboClass2.clear()
            self.ui.comboClass3.clear()

    def update(self, i):
        """更新界面上的进度条和label，用于反映已经爬到的数据量"""
        print 'Update', i
        self.ui.progress.setValue(i)
        # QtGui.qApp.processEvents()
        self.ui.labelp.setText(str(i) + '/' + str(self.totalNum))

    def sliderPageTimeUpdate(self, i):
        """slider的回调函数，用于设置爬取页面的时间间隔"""
        self.sleep = float(i) / 10 + 0.1
        self.ui.labeltime.setText(str(self.sleep))

    def setDir(self):
        """用于设置数据的保存路径"""
        self.path = QtGui.QFileDialog.getExistingDirectory(self,
                                                           "Open a folder",
                                                           self.path,
                                                           QtGui.QFileDialog.ShowDirsOnly)
        print self.path
        self.ui.labelSave.setText(self.path)


def main():
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
