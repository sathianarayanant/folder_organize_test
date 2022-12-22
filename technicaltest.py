import os
import sys
import shutil
import json
from PyQt5 import QtGui,QtWidgets,QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

from pathlib import Path
import time
from datetime import datetime

class createUI(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.executeUI()
        self.setWindowTitle('Folder Organizer')
        self.setFixedSize(740,430)
        self.filetypeList = []

    def executeUI(self):

        self.inputpathBox = QLineEdit(self)
        self.outputpathBox = QLineEdit(self)
        self.spaceLabel = QLabel ("",self)
        self.inpbrowseButton = QPushButton ("Select Input Path")
        self.outbrowseButton = QPushButton ("Select Output Path")
        self.progress_label =QLabel("Copying Status", self)
        self.progress_bar =QtWidgets.QProgressBar(self)
        self.progress_bar.setGeometry(60,30,430,30)
        self.progress_bar.setMaximum(100)

        self.formL= QFormLayout(self)
        
        self.formL.addRow(self.spaceLabel)
        self.formL.addRow(self.inpbrowseButton,self.inputpathBox)
        self.formL.addRow(self.outbrowseButton,self.outputpathBox)
        self.formL.addRow(self.spaceLabel)

        self.formL.addRow(self.spaceLabel)
        self.formL.addRow(self.progress_label)
        self.formL.addRow(self.progress_bar)
        self.formL.addRow(self.spaceLabel)

        self.formL.addRow(self.spaceLabel)
        self.copytextFile = QtWidgets.QTextEdit('',self)
        self.copytextFile.setGeometry(60,140,395,250)
        self.copytextFile.setReadOnly(True)

        self.formL.addRow(self.copytextFile)
        self.formL.addRow(self.spaceLabel)
        
        self.organizeLabel = QLabel ('Click on PROCEED to organize Files in Separate Folders',self)
        self.proceedButton = QPushButton ('PROCEED')
        self.cancelButton = QPushButton ('Cancel')

        self.formL.addRow(self.spaceLabel)
        self.formL.addRow(self.organizeLabel)
        self.formL.addRow(self.cancelButton,self.proceedButton)
        self.formL.addRow(self.spaceLabel)

        self.proceedButton.clicked.connect(self.explorePath)
        self.cancelButton.clicked.connect(self.cancelFun)
        self.inpbrowseButton.clicked.connect(self.selectInput)
        self.outbrowseButton.clicked.connect(self.selectOutput)
        self.setLayout(self.formL)

    def selectInput(self):
        inputFolderChosen = QFileDialog.getExistingDirectory(self,"select Folder")
        self.inputpathBox.setText(os.path.realpath(inputFolderChosen))

    def selectOutput(self):
        outputFolderChosen = QFileDialog.getExistingDirectory(self,"select Folder")
        self.outputpathBox.setText(os.path.realpath(outputFolderChosen))
        
    def explorePath(self):
        path= self.inputpathBox.text()
        destiPath = self.outputpathBox.text()
        if path and destiPath:
            for root,dirs,files in os.walk(path):
                if files:
                    fileStem = Path(files[0]).stem
                    if Path(fileStem).suffix:
                        fileStem = Path(fileStem).stem
                    if "_" in fileStem:
                        filenamesplitList = fileStem.split("_")
                    for f in files:
                        fileExt= Path(f).suffix[1:]
                        self.filetypeList.append(fileExt)
                        self.filetypeList = list(dict.fromkeys(self.filetypeList))
            if self.filetypeList and filenamesplitList:
                #try:
                taskPath = self.createFolders(filenamesplitList)
                self.copyFiles(path,taskPath)
                self.generateJson(taskPath,destiPath)
                # except:
                #     print('unable to organize in required folders')
                #     msg = QMessageBox()
                #     msg.setText('unable to organize in required folders')
                #     msg.exec_()
            else:
                print('file name format not supported for required folder structure')
                msg = QMessageBox()
                msg.setText('file name format not supported for required folder structure')
                msg.exec_()
        else:
            print('please select input and output path...')
            msg = QMessageBox()
            msg.setText('please select input and output path...')
            msg.exec_()
            return

    def cancelFun(self):
        self.close()

    def createFolders(self,filenamesplitList):
        destiPath= self.outputpathBox.text()
        self.projectName = filenamesplitList[0]
        self.shotName = filenamesplitList[0]+"_"+filenamesplitList[1]
        self.taskName = filenamesplitList[2]
        projPath = os.path.join(destiPath,self.projectName)
        time = str(datetime.now()).split(".")[0][:-3]
        datetimeStamp = time.replace("-","").replace(" ","").replace(":","")
        datetimePath = os.path.join(projPath,datetimeStamp)
        shotPath = os.path.join(datetimePath,self.shotName)
        taskPath = os.path.join(shotPath,self.taskName)
        
        print(taskPath)
        if os.path.exists(destiPath) == True:
            if os.path.exists(taskPath) == False:
                os.makedirs(taskPath)
            for ext in self.filetypeList:
                if os.path.exists(os.path.join(taskPath,ext.upper())) == False:
                    os.mkdir(os.path.join(taskPath,ext.upper()))
        else:
            print('given output path does not exist')
            msg = QMessageBox()
            msg.setText('given output path does not exist')
            msg.exec_()
            return
        return taskPath

    def copyFiles(self,path,taskPath):
        for root,dirs,files in os.walk(path):
            for i in range(len(files)):
                fileExt=Path(files[i]).suffix[1:]
                if os.path.exists(os.path.join(taskPath,fileExt)) == True:
                    finaldestiPath= os.path.join(taskPath,fileExt)
                    if os.path.exists(os.path.join(finaldestiPath,files[i]))== False:
                        if fileExt:
                            formulaVar = 100/len(files)*i
                            QApplication.processEvents()
                            shutil.copyfile(os.path.join(root,files[i]),os.path.join(finaldestiPath,files[i]))
                            self.progress_bar.setValue(formulaVar)
                            self.copytextFile.append(files[i])
        print('done')
        self.progress_bar.setValue(100)
        msg = QMessageBox()
        msg.setText('Folders organized now!')
        msg.exec_()

    def generateJson(self,taskPath,destiPath):
        filetypeDict = {}
        jsonDict = {}
        for root,dirs,files in os.walk(taskPath):
            for f in files:
                if Path(f).suffix[1:].upper() == os.path.basename(os.path.dirname(os.path.join(root,f))):
                    filetypeDict[os.path.basename(os.path.dirname(os.path.join(root,f)))] = os.listdir( os.path.dirname(os.path.join(root,f)) )
        jsonDict[os.path.basename(taskPath)] = filetypeDict
        iterPath = os.path.dirname(taskPath)
        print('iter path:',iterPath)
        while iterPath != destiPath:
            for fold in os.listdir(iterPath):
                print(os.listdir(iterPath),iterPath)
                if fold.isnumeric() == True:
                    fold = os.listdir(iterPath)[len( os.listdir(iterPath) )-1]
                    print('Fold:',fold)
                tempDict = {}
                try:
                    if len( os.listdir(os.path.join(iterPath,fold)) ) == 1:
                        if fold == os.path.basename(taskPath):
                            tempDict[fold] = jsonDict
                            jsonDict = tempDict
                        else:
                            tempDict[fold] = jsonDict
                            jsonDict = tempDict
                except:
                    pass
            iterPath = os.path.dirname(iterPath)
                
        if iterPath == destiPath:
            for fold in os.listdir(iterPath):
                tempDict = {}
                if len( os.listdir(os.path.join(iterPath,fold)) ) == 1:
                    if os.listdir(os.path.join(iterPath,fold))[0] in list(jsonDict.keys()):
                        tempDict[fold] = jsonDict
                        jsonDict = tempDict
        print("\n",jsonDict)
        with open( os.path.join(os.path.dirname(destiPath),'result.json'),'w' ) as file:
            json.dump(jsonDict,file,indent=4)

app= QApplication(sys.argv)
appln= createUI()
appln.show ()
sys.exit(app.exec_())

