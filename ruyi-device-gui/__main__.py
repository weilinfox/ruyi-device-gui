#!/usr/bin/env python3
# Copyright 2017-2024 白玉楼製作所 <sakurakaze@gensokyo.ac.cn>
# Copyright 2023-2024 桜風の狐 <caiweilin@iscas.ac.cn>

import logging
import os
import re
import sys

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (QApplication, QButtonGroup, QComboBox,  QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                               QPushButton, QRadioButton, QTextEdit, QVBoxLayout, QWidget)


class RuyiGui(QWidget):
    def __init__(self, ruyi):
        super().__init__()
        self.ruyi = ruyi
        self.initUI()

    def initUI(self):
        # 窗口
        self.setWindowTitle('ruyi device provision 公众科学日演示程序 [ by 樱风之狐 from 第三测试小队 ]')
        self.setGeometry(100, 100, 1000, 600)
        self.setMinimumSize(self.width(), self.height())
        self.setMaximumSize(self.width(), self.height())
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        mainLayout = QHBoxLayout()

        # 左部区域 显示输出
        demoLayout = QVBoxLayout()
        self.ruyiOutEdit = QTextEdit()
        self.ruyiOutEdit.append("ruyi 程序将在这里运行...\n\n"
                                "RuyiSDK 是一个旨在提供给一个一体化集成开发环境的产品计划。\n\n"
                                "从 2023 年开始筹备，计划用三年时间为 RISC-V 开发者提供一个完整的、\n"
                                "全家桶式的全功能开发环境。\n\n"
                                "ruyi 包管理器是 RuyiSDK 的一部分，用于与在线软件源交互，使开发者\n"
                                "能够搜索、安装、更新和管理 ruyi 软件包\n\n"
                                "ruyi device provision 则是 ruyi 包管理器中专用于管理开发板系统镜像\n"
                                "的功能组件。\n\n"
                                "你可以在这个演示程序中使用和了解 ruyi device provision 的管理功能，\n"
                                "也可以打开系统的终端模拟器，脱离该演示程序直接运行该命令。\n\n"
                                "亦可以直接运行 ruyi 命令，使用完整功能。\n\n"
                                "RuyiSDK 官方网站： https://ruyisdk.org/\n"
                                "RuyiSDK 项目主页： https://github.com/ruyisdk\n"
                                "RuyiSDK 支持矩阵： https://ruyisdk.org/supported/\n"
                                "RuyiSDK 在线文档： https://ruyisdk.github.io/docs/zh/introduction/")
        self.ruyiOutEdit.setFixedWidth(600)
        # self.textEdit.setAcceptRichText(True)
        self.ruyiOutEdit.setReadOnly(True)
        self.ruyiOutEdit.setLineWrapMode(self.ruyiOutEdit.LineWrapMode.NoWrap)
        self.noteLabel = QLabel("这是 ruyi device provision 公众科学日演示程序\nApache-2.0 license\n"
                                "https://github.com/weilinfox/ruyi-device-gui")
        self.noteLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.noteLabel.setFixedHeight(75)
        self.noteLabel.setFixedWidth(600)
        demoLayout.addWidget(self.ruyiOutEdit)
        demoLayout.addWidget(self.noteLabel)

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
        boardButton = QPushButton("确定")
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
        variantButton = QPushButton("确定")
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
        mirrorButton = QPushButton("确定")
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
        diskButton = QPushButton("确定")
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

        mainLayout.addLayout(demoLayout)
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
        self.ruyiOutEdit.clear()
        self.ruyiOutEdit.append("$ {} device provision\n".format(self.ruyi))
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
        self.ruyiOutEdit.append("\nruyi 进程已结束 ({})".format(self.process.exitCode()))
        if self.process.exitCode() != 0 and self.process.exitCode() != 9 :
            self.noteLabel.setText("ruyi device provision 进程已经退出，且返回值并不为 0\n可以阅读打印的信息以获知原因")

    def endRuyi(self):
        self.process.kill()
        self.noteLabel.setText("已经结束 ruyi device provision 的运行，还可以重新运行它\n"
                               "这是 ruyi device provision 公众科学日演示程序\nApache-2.0 license")

    def sendInput(self):
        text = self.inputLineEdit.text() + "\n"
        self.ruyiOutEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.inputLineEdit.clear()

    def sendContinue(self):
        if self.continueCheck.checkedId():
            text = "y\n"
        else:
            text = "n\n"
        self.ruyiOutEdit.insertPlainText(text)
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
        self.ruyiOutEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.proceedCheckNo.setEnabled(False)
        self.proceedCheckYes.setEnabled(False)
        self.proceedButtom.setEnabled(False)
        self.noteLabel.setText("正在下载...\n可以喝杯咖啡或者出去溜达一下 :D")

    def sendFlashing(self, send):
        if send:
            text = "y\n"
        else:
            text = "n\n"
        self.ruyiOutEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)

    def sendDiskDevice(self):
        text = self.flashCombos[-1].currentText() + "\n"
        self.ruyiOutEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.flashCombos[-1].setEnabled(False)
        self.flashButtons[-1].setEnabled(False)

    def sendNextStep(self):
        text = str(self.flashCombos[self.ruyiStep].currentIndex() + 1) + "\n"
        self.ruyiOutEdit.insertPlainText(text)
        self.process.write(text.encode())
        logging.debug("Sent " + text)
        self.flashCombos[self.ruyiStep].setEnabled(False)
        self.flashButtons[self.ruyiStep].setEnabled(False)
        self.ruyiStep += 1

    def onReadyRead(self):
        # 处理输出
        output = self.process.readAll().data().decode()
        self.ruyiOutEdit.insertPlainText(output)
        self.ruyiOutEdit.moveCursor(QTextCursor.MoveOperation.End)
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
                self.noteLabel.setText("ruyi device provision 命令已经开始运行\n你可以在右侧通过按钮输入，也可以由输入框手动输入\n"
                                       "或是直接结束运行")
                break
            elif sl.strip() == "Proceed? (y/N)":
                logging.debug("Get proceed")
                self.proceedCheckNo.setEnabled(True)
                self.proceedCheckYes.setEnabled(True)
                self.proceedCheckYes.setChecked(True)
                self.proceedButtom.setEnabled(True)
                self.ruyiItems.clear()
                self.noteLabel.setText("你已经选择好了镜像\n如果在这里继续，则会开始下载它，这需要一段时间的等待\n"
                                       "不过也有可能，这个镜像上次就已经下载下来了")
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
                        self.noteLabel.setText("镜像已经下载并解包好，你要选择一个磁盘来写入\n不要选错盘哦")
                    else:
                        self.flashCombos[-1].addItem('No available disk found')
                        self.noteLabel.setText("镜像已经下载并解包好，但是演示程序并没有发现可供写入的磁盘\n"
                                               "当然你也可以手动指定磁盘路径")
                        QMessageBox.warning(self, "没有找到可供写入的磁盘",
                                            "演示程序没有找到可供镜像写入的磁盘\n请检查磁盘是否插入，或选择手动指定",
                                            QMessageBox.StandardButton.Ok)
            elif sl.strip() == "Proceed with flashing? (y/N)":
                self.ruyiItems.clear()
                diskName = self.flashCombos[-1].currentText()
                if diskName.strip():
                    self.noteLabel.setText("再次确认 {} 是你想要写入的磁盘\n"
                                           "这个操作貌似没有后悔药吃的".format(diskName))
                    ret = QMessageBox.information(self, "确认磁盘刷写",
                                                  "确认向 {} 写入镜像？\n该操作将永久擦除该磁盘的已有数据".format(diskName),
                                                  QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Abort)
                else:
                    self.noteLabel.setText("这个镜像并不是用来直接向磁盘 dd 的\n"
                                           "这是一个借助其他工具写入设备的镜像")
                    ret = QMessageBox.information(self, "确认磁盘刷写", "确认设备刷写？该操作将永久擦除该设备的已有数据",
                                                  QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Abort)
                self.sendFlashing(ret == QMessageBox.StandardButton.Ok)
            elif re.match(r"Do you want to retry the command with.*sudo.*\? \(y/N\)", sl.strip()):
                self.ruyiItems.clear()
                self.noteLabel.setText("使用普通用户权限写入失败了\n这可能是因为这个操作需要 root 权限才能完成\n"
                                       "此时将尝试使用 sudo 命令提权")
                ret = QMessageBox.information(self, "确认使用 sudo 提权",
                                              "操作失败，这可能是由于缺少 root 权限导致的\n是否使用 sudo 命令提权？",
                                              QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Abort)
                self.sendFlashing(ret == QMessageBox.StandardButton.Ok)
            elif sl.strip() == "Is the device identified by fastboot now? (y/N)":
                output = os.popen('fastboot devices 2>&1').read()
                self.ruyiItems.clear()
                self.noteLabel.setText("这是一个使用 fastboot 工具重置设备的镜像\n"
                                       "你需要检查 fastboot devices 命令的输出，以确认 fastboot 能够正常找到需要刷写的设备")
                if output.strip() == "":
                    output = "<输出为空>"
                ret = QMessageBox.information(self, "确认 fastboot 输出",
                                              "fastboot devices 命令的输出如下：\n" + output + "\n是否继续？",
                                              QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Abort)
                self.sendFlashing(ret == QMessageBox.StandardButton.Ok)
            elif sl.strip() == "It seems the flashing has finished without errors.":
                self.ruyiItems.clear()
                os.system('sync')
                self.noteLabel.setText("镜像刷写成功，这是好的")
                QMessageBox.information(self, "刷写成功", "镜像刷写成功", QMessageBox.StandardButton.Ok)
            elif sl.strip() == "NOTE: You have to consult the RuyiSDK Support Matrix documentation":
                self.ruyiItems.clear()
                self.noteLabel.setText("有些开发板并不能运行 Linux 操作系统，或者上游并没有给出相关镜像\n"
                                       "还有一些开发板是用户客制化的，需要用户/开发者自行编程\n"
                                       "ruyi 为它们提供了文档支持，在 ruyi device provision 的输出中可以看到详细信息")
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
                self.ruyiItems.clear()
                if self.ruyiStep == 0:
                    self.noteLabel.setText("选择你的板卡型号\n你可以在右侧下拉列表中选择，也可以由输入框手动输入\n"
                                           "或是直接结束运行")
                elif self.ruyiStep == 1:
                    self.noteLabel.setText("选择你的板卡类型\n你可以在右侧下拉列表中选择，也可以由输入框手动输入\n"
                                           "或是直接结束运行")
                elif self.ruyiStep == 2:
                    self.noteLabel.setText("选择可用的安装镜像\n你可以在右侧下拉列表中选择，也可以由输入框手动输入\n"
                                           "或是直接结束运行")
                else:
                    self.noteLabel.setText("欸？")
                break


if __name__ == "__main__":

    binary = 'ruyi'
    logging.getLogger().setLevel(logging.DEBUG)

    app = QApplication(sys.argv)
    ruyiGui = RuyiGui(binary)
    ruyiGui.show()
    sys.exit(app.exec_())
