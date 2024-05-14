#!/usr/bin/env python3
# Copyright 2017-2024 白玉楼製作所 <sakurakaze@gensokyo.ac.cn>
# Copyright 2023-2024 桜風の狐 <caiweilin@iscas.ac.cn>

import logging
import os
import re
import sys

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (QApplication, QButtonGroup, QComboBox,  QHBoxLayout, QLineEdit, QMessageBox, QPushButton,
                               QRadioButton, QTextEdit, QVBoxLayout, QWidget)


class RuyiGui(QWidget):
    def __init__(self, ruyi):
        super().__init__()
        self.ruyi = ruyi
        self.initUI()

    def initUI(self):
        # 窗口
        self.setWindowTitle('ruyi device provision 演示程序 [ by 桜風の狐 at 白玉楼製作所 ]')
        self.setGeometry(100, 100, 1000, 600)
        self.setMinimumSize(self.width(), self.height())
        self.setMaximumSize(self.width(), self.height())
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        mainLayout = QHBoxLayout()

        # 左部区域 显示输出
        self.textEdit = QTextEdit()
        self.textEdit.setFixedWidth(600)
        # self.textEdit.setAcceptRichText(True)
        self.textEdit.setReadOnly(True)
        self.textEdit.setLineWrapMode(self.textEdit.LineWrapMode.NoWrap)
        mainLayout.addWidget(self.textEdit)

        # 右部区域 用户控制
        userLayout = QVBoxLayout()
        userLayout.setContentsMargins(5, 0, 0, 0)
        self.runButton = QPushButton('运行 ruyi device provision')
        self.runButton.setFixedHeight(60)
        self.runButton.clicked.connect(self.runCommand)

        # Continue
        continueLayout = QHBoxLayout()
        continueLayout.setContentsMargins(60, 0, 0, 0)
        self.continueCheck = QButtonGroup()
        self.continueCheckYes = QRadioButton("是")
        self.continueCheckNo = QRadioButton("否")
        self.continueCheckNo.setEnabled(False)
        self.continueCheckYes.setEnabled(False)
        self.continueCheck.addButton(self.continueCheckYes, 1)
        self.continueCheck.addButton(self.continueCheckNo, 0)
        self.continueButtom = QPushButton("继续")
        self.continueButtom.setFixedHeight(36)
        self.continueButtom.setEnabled(False)
        self.continueButtom.clicked.connect(self.sendContinue)
        continueLayout.addWidget(self.continueCheckYes)
        continueLayout.addWidget(self.continueCheckNo)
        continueLayout.addWidget(self.continueButtom)

        # 板卡选择
        self.flashCombos = []
        self.flashButtons = []
        boardLayout = QHBoxLayout()
        boardCombo = QComboBox()
        boardButton = QPushButton("确信")
        boardCombo.setEnabled(False)
        boardButton.setEnabled(False)
        boardButton.clicked.connect(self.sendNextStep)
        boardCombo.setFixedWidth(280)
        boardCombo.setFixedHeight(36)
        boardButton.setFixedHeight(36)
        self.flashCombos.append(boardCombo)
        self.flashButtons.append(boardButton)
        boardLayout.addWidget(boardCombo)
        boardLayout.addWidget(boardButton)

        # 品种选择
        variantLayout = QHBoxLayout()
        variantCombo = QComboBox()
        variantButton = QPushButton("确信")
        variantCombo.setEnabled(False)
        variantButton.setEnabled(False)
        variantButton.clicked.connect(self.sendNextStep)
        variantCombo.setFixedWidth(280)
        variantCombo.setFixedHeight(36)
        variantButton.setFixedHeight(36)
        self.flashCombos.append(variantCombo)
        self.flashButtons.append(variantButton)
        variantLayout.addWidget(variantCombo)
        variantLayout.addWidget(variantButton)

        # 镜像选择
        mirrorLayout = QHBoxLayout()
        mirrorCombo = QComboBox()
        mirrorButton = QPushButton("确信")
        mirrorCombo.setEnabled(False)
        mirrorButton.setEnabled(False)
        mirrorButton.clicked.connect(self.sendNextStep)
        mirrorCombo.setFixedWidth(280)
        mirrorCombo.setFixedHeight(36)
        mirrorButton.setFixedHeight(36)
        self.flashCombos.append(mirrorCombo)
        self.flashButtons.append(mirrorButton)
        mirrorLayout.addWidget(mirrorCombo)
        mirrorLayout.addWidget(mirrorButton)

        # 磁盘选择
        diskLayout = QHBoxLayout()
        diskCombo = QComboBox()
        diskButton = QPushButton("确信")
        diskCombo.setEnabled(False)
        diskButton.setEnabled(False)
        diskButton.clicked.connect(self.sendDiskDevice)
        diskCombo.setFixedWidth(280)
        diskCombo.setFixedHeight(36)
        diskButton.setFixedHeight(36)
        self.flashCombos.append(diskCombo)
        self.flashButtons.append(diskButton)
        diskLayout.addWidget(diskCombo)
        diskLayout.addWidget(diskButton)

        # Proceed
        proceedLayout = QHBoxLayout()
        proceedLayout.setContentsMargins(60, 0, 0, 0)
        self.proceedCheck = QButtonGroup()
        self.proceedCheckYes = QRadioButton("是")
        self.proceedCheckNo = QRadioButton("否")
        self.proceedCheckNo.setEnabled(False)
        self.proceedCheckYes.setEnabled(False)
        self.proceedCheck.addButton(self.proceedCheckYes, 1)
        self.proceedCheck.addButton(self.proceedCheckNo, 0)
        self.proceedButtom = QPushButton("继续")
        self.proceedButtom.setFixedHeight(36)
        self.proceedButtom.setEnabled(False)
        self.proceedButtom.clicked.connect(self.sendProceed)
        proceedLayout.addWidget(self.proceedCheckYes)
        proceedLayout.addWidget(self.proceedCheckNo)
        proceedLayout.addWidget(self.proceedButtom)

        # 手动输入
        inputLayout = QHBoxLayout()
        self.inputLineEdit = QLineEdit()
        self.inputLineEdit.setPlaceholderText("手动输入")
        self.inputLineEdit.setFixedWidth(280)
        self.inputLineEdit.setFixedHeight(36)
        self.sendButton = QPushButton('发送')
        self.restartButton = QPushButton('结束 ruyi device provision')
        self.restartButton.setFixedHeight(60)
        self.inputLineEdit.setEnabled(False)
        self.sendButton.setEnabled(False)
        self.restartButton.setEnabled(False)
        self.sendButton.clicked.connect(self.sendInput)
        self.restartButton.clicked.connect(self.endRuyi)
        inputLayout.addWidget(self.inputLineEdit)
        inputLayout.addWidget(self.sendButton)

        userLayout.addWidget(self.runButton)
        userLayout.addLayout(continueLayout)
        userLayout.addLayout(boardLayout)
        userLayout.addLayout(variantLayout)
        userLayout.addLayout(mirrorLayout)
        userLayout.addLayout(proceedLayout)
        userLayout.addLayout(diskLayout)
        userLayout.addLayout(inputLayout)
        userLayout.addWidget(self.restartButton)

        mainLayout.addLayout(userLayout)
        self.setLayout(mainLayout)

        # RUYI QProcess
        self.process = QProcess(self)
        # 合并 stdout 和 stderr
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.onReadyRead)
        self.process.finished.connect(self.endCommand)

    def runCommand(self):
        self.textEdit.clear()
        self.textEdit.append("$ {} device provision\n".format(self.ruyi))
        self.process.start(self.ruyi, ['device', 'provision'])
        self.runButton.setEnabled(False)
        self.inputLineEdit.setEnabled(True)
        self.sendButton.setEnabled(True)
        self.restartButton.setEnabled(True)
        for it in self.flashCombos:
            it.clear()
            it.setEnabled(False)
        for it in self.flashButtons:
            it.setEnabled(False)
        self.ruyiStep = 0
        self.ruyiItems = []

    def endCommand(self):
        self.runButton.setEnabled(True)
        self.restartButton.setEnabled(False)
        self.inputLineEdit.setEnabled(False)
        self.sendButton.setEnabled(False)
        self.continueCheckNo.setEnabled(False)
        self.continueCheckYes.setEnabled(False)
        self.continueButtom.setEnabled(False)
        self.proceedCheckNo.setEnabled(False)
        self.proceedCheckYes.setEnabled(False)
        self.proceedButtom.setEnabled(False)
        for it in self.flashCombos:
            it.setEnabled(False)
        for it in self.flashButtons:
            it.setEnabled(False)
        self.textEdit.append("\nruyi 进程已结束 ({})".format(self.process.exitCode()))

    def endRuyi(self):
        self.process.kill()

    def sendInput(self):
        text = self.inputLineEdit.text() + "\n"
        self.textEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.inputLineEdit.clear()

    def sendContinue(self):
        if self.continueCheck.checkedId():
            text = "y\n"
        else:
            text = "n\n"
        self.textEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.continueCheckNo.setEnabled(False)
        self.continueCheckYes.setEnabled(False)
        self.continueButtom.setEnabled(False)

    def sendProceed(self):
        if self.proceedCheck.checkedId():
            text = "y\n"
        else:
            text = "n\n"
        self.textEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.proceedCheckNo.setEnabled(False)
        self.proceedCheckYes.setEnabled(False)
        self.proceedButtom.setEnabled(False)

    def sendFlashing(self, send):
        if send:
            text = "y\n"
        else:
            text = "n\n"
        self.textEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)

    def sendDiskDevice(self):
        text = self.flashCombos[-1].currentText() + "\n"
        self.textEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.flashCombos[-1].setEnabled(False)
        self.flashButtons[-1].setEnabled(False)

    def sendNextStep(self):
        text = str(self.flashCombos[self.ruyiStep].currentIndex() + 1) + "\n"
        self.textEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.flashCombos[self.ruyiStep].setEnabled(False)
        self.flashButtons[self.ruyiStep].setEnabled(False)
        self.ruyiStep += 1

    def onReadyRead(self):
        # 处理输出
        output = self.process.readAll().data().decode()
        self.textEdit.insertPlainText(output)
        self.textEdit.moveCursor(QTextCursor.MoveOperation.End)
        self.onNextStep(output)

    def onNextStep(self, output):
        splitOut = output.split('\n')
        for sl in splitOut:
            if re.match(r"^  [0-9]+\. .*$", sl):
                self.ruyiItems.append(re.match(r"^  [0-9]+\. (.*)$", sl).group(1).strip())
            elif sl.strip() == "Continue? (y/N)":
                logging.debug("Get continue")
                self.continueCheckNo.setEnabled(True)
                self.continueCheckYes.setEnabled(True)
                self.continueCheckYes.setChecked(True)
                self.continueButtom.setEnabled(True)
                self.ruyiItems.clear()
                break
            elif sl.strip() == "Proceed? (y/N)":
                logging.debug("Get proceed")
                self.proceedCheckNo.setEnabled(True)
                self.proceedCheckYes.setEnabled(True)
                self.proceedCheckYes.setChecked(True)
                self.proceedButtom.setEnabled(True)
                self.ruyiItems.clear()
                break
            elif sl.strip() == "Please give the path for the target's whole disk:":
                self.ruyiItems.clear()
                output = (os.popen('lsblk --ascii --paths --tree=NAME --noheadings --output NAME,TYPE,MOUNTPOINTS')
                          .read())
                output = output.split("\n")
                if len(output) < 2:
                    self.flashCombos[-1].addItem("Error executing lsblk")
                else:
                    disk = 0
                    disks = []
                    while disk < len(output) and output[disk]:
                        part = disk + 1
                        mounted = False
                        isDisk = False
                        if output[disk].split()[1] == "disk":
                            isDisk = True
                        while part < len(output) and output[part] and output[part][0] in ['|', '`']:
                            if len(output[part].split()) > 2:
                                mounted = True
                            part += 1
                        if isDisk and not mounted:
                            disks.append(output[disk].split()[0])
                        disk = part
                    if len(disks):
                        self.flashCombos[-1].addItems(disks)
                        self.flashCombos[-1].setEnabled(True)
                        self.flashButtons[-1].setEnabled(True)
                    else:
                        self.flashCombos[-1].addItem('No available disk found')
                        QMessageBox.warning(self, "没有找到可供写入的磁盘",
                                            "演示程序没有找到可供镜像写入的磁盘\n请检查磁盘是否插入，或选择手动指定",
                                            QMessageBox.StandardButton.Ok)
            elif sl.strip() == "Proceed with flashing? (y/N)":
                self.ruyiItems.clear()
                diskName = self.flashCombos[-1].currentText()
                if diskName.strip():
                    ret = QMessageBox.information(self, "确认磁盘刷写",
                                                  "确认向 {} 写入镜像？\n该操作将永久擦除该磁盘的已有数据".format(diskName),
                                                  QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Abort)
                else:
                    ret = QMessageBox.information(self, "确认磁盘刷写", "确认？", QMessageBox.StandardButton.Ok,
                                                  QMessageBox.StandardButton.Abort)
                self.sendFlashing(ret == QMessageBox.StandardButton.Ok)
            elif re.match(r"Do you want to retry the command with.*sudo.*\? \(y/N\)", sl.strip()):
                self.ruyiItems.clear()
                ret = QMessageBox.information(self, "确认使用 sudo 提权",
                                              "操作失败，这可能是由于缺少 root 权限导致的\n是否使用 sudo 命令提权？",
                                              QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Abort)
                self.sendFlashing(ret == QMessageBox.StandardButton.Ok)
            elif sl.strip() == "Is the device identified by fastboot now? (y/N)":
                output = os.popen('fastboot devices 2>&1').read()
                self.ruyiItems.clear()
                ret = QMessageBox.information(self, "确认 fastboot 输出",
                                              "fastboot devices 命令的输出如下：\n" + output + "是否继续？",
                                              QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Abort)
                self.sendFlashing(ret == QMessageBox.StandardButton.Ok)
            elif sl.strip() == "It seems the flashing has finished without errors.":
                self.ruyiItems.clear()
                os.system('sync')
                QMessageBox.information(self, "刷写成功", "镜像刷写成功", QMessageBox.StandardButton.Ok)
            elif sl.strip() == "NOTE: You have to consult the RuyiSDK Support Matrix documentation":
                self.ruyiItems.clear()
                QMessageBox.information(self, "仅文档支持", "上游并没有提供可用的镜像，您需要阅读 ruyi 支持矩阵文档来了解更多信息。",
                                        QMessageBox.StandardButton.Ok)
            elif re.match(r"^Choice\? \(1-[0-9]+\)", sl.strip()):
                logging.debug("Get choice")
                item = re.match(r"^Choice\? \(1-([0-9]+)\)", sl.strip()).group(1)
                if item == str(len(self.ruyiItems)):
                    logging.debug("Choose Please")
                    self.flashCombos[self.ruyiStep].addItems(self.ruyiItems)
                    self.flashCombos[self.ruyiStep].setEnabled(True)
                    self.flashButtons[self.ruyiStep].setEnabled(True)
                self.inputLineEdit.setPlaceholderText("手动输入")
                self.ruyiItems.clear()
                break


if __name__ == "__main__":

    binary = 'ruyi'
    logging.getLogger().setLevel(logging.DEBUG)

    app = QApplication(sys.argv)
    ruyiGui = RuyiGui(binary)
    ruyiGui.show()
    sys.exit(app.exec_())
