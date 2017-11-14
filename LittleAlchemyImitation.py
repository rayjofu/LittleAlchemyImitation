#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtCore import (QByteArray, QDataStream, QFile, QIODevice, QMimeData,
        QPoint, QRect, QRectF, Qt, QTextStream)
from PyQt5.QtGui import (QCursor, QDrag, QFont, QFontMetrics, QImage, QPainter,
        QPalette, QPixmap, qRgba)
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

import fridgemagnets_rc


class DragLabel(QLabel):
    def __init__(self, text, parent):
        super(DragLabel, self).__init__(parent)

        metric = QFontMetrics(self.font())
        size = metric.size(Qt.TextSingleLine, text)

        image = QImage(size.width() + 12, size.height() + 12,
                QImage.Format_ARGB32_Premultiplied)
        image.fill(qRgba(0, 0, 0, 0))

        font = QFont()
        font.setStyleStrategy(QFont.ForceOutline)

        painter = QPainter()
        painter.begin(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.white)
        painter.drawRoundedRect(
                QRectF(0.5, 0.5, image.width()-1, image.height()-1),
                25, 25, Qt.RelativeSize)

        painter.setFont(font)
        painter.setBrush(Qt.black)
        painter.drawText(QRect(QPoint(6, 6), size), Qt.AlignCenter, text)
        painter.end()

        self.setPixmap(QPixmap.fromImage(image))
        self.labelText = text
        self.setAttribute(Qt.WA_DeleteOnClose)

class DragWidget(QWidget):
    def __init__(self, win_x=600, win_y=400, parent=None):
        super(DragWidget, self).__init__(parent)

        dictionaryFile = QFile('recipe_input.txt')
        dictionaryFile.open(QFile.ReadOnly)

        self.recipe = {}
        
        x = 5
        y = win_y / 3 + 5

        # read recipes from file
        tempHash = {}
        for line in QTextStream(dictionaryFile).readAll().split():
            result,formula = line.split("=")
            # avoid making duplicate labels for result
            if result not in tempHash:
                wordLabel = DragLabel(result, self)
                wordLabel.show()
                wordLabel.move(x, y)
                x += wordLabel.width() + 2
                if x >= 530:
                    x = 5
                    y += wordLabel.height() + 2
            else:
                wordLabel = tempHash[result]
            # split formula into components
            components = formula.split("+")
            if len(components) > 1:
                self.recipe[formula] = wordLabel
                self.recipe[components[1]+"+"+components[0]] = wordLabel
                wordLabel.hide()
                tempHash[result] = wordLabel
            else:
                wordLabel.show()
            

        newPalette = self.palette()
        newPalette.setColor(QPalette.Window, Qt.white)
        self.setPalette(newPalette)

        self.setFixedSize(win_x, win_y)
        self.setWindowTitle("Little Alchemy Imitation")
        self.setAcceptDrops(True)

        # start location of drag
        # 0 => ingredients section, 1 => craft slot 1, 2 => craft slot 2, 3=> craft result
        self.startLocation = None
        # end location of drag
        # 0 => ingredients section, 1 => craft slot 1, 2 => craft slot 2, 3=> craft result
        self.endLocation = None

        # label in slot1
        self.slot1 = None
        # label in slot2
        self.slot2 = None
        # label in result
        self.result = None

        # for count display
        self.count = 0
        self.total = len(tempHash)
        self.countDisplay = QLabel(str(self.count) + "/" + str(self.total), self)
        self.countDisplay.show()
        self.countDisplay.setAttribute(Qt.WA_DeleteOnClose)
        self.centerLabel(self.countDisplay, self.width()/2, self.height()*5/6)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        # border
        qp.drawLine(0, self.height()/3, self.width(), self.height()/3)
        # slot 1
        qp.drawRect(self.width()*3/18, self.height()/12, self.width()/9, self.height()/6)
        # plus
        qp.drawLine(self.width()*5.5/18, self.height()*2/12, self.width()*6.5/18, self.height()*2/12)
        qp.drawLine(self.width()*6/18, self.height()*2/12 - self.width()/36, self.width()*6/18, self.height()*2/12+self.width()/36)
        # slot 2
        qp.drawRect(self.width()*7/18, self.height()/12, self.width()/9, self.height()/6)
        # arrow
        qp.drawLine(self.width()*10/18, self.height()*2/12, self.width()*11/18, self.height()*2/12)
        qp.drawLine(self.width()*10.5/18, self.height()*1.75/12, self.width()*11/18, self.height()*2/12)
        qp.drawLine(self.width()*10.5/18, self.height()*2.25/12, self.width()*11/18, self.height()*2/12)
        # result
        qp.drawRect(self.width()*12/18, self.height()/12, self.width()/9, self.height()/6)
        qp.end()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-fridgemagnet'):
            if event.source() in self.children():
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        elif event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-fridgemagnet'):
            if event.source() == self:
                # store location of drag end
                self.endLocation = self.getLocation(self.mapFromGlobal(QCursor().pos()))
##                print(endLocation)
                # set action depending on drag start and end
                self.setAction(event, self.startLocation, self.endLocation)
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-fridgemagnet'):
            mime = event.mimeData()
            itemData = mime.data('application/x-fridgemagnet')
            dataStream = QDataStream(itemData, QIODevice.ReadOnly)

            text = QByteArray()
            offset = QPoint()
            dataStream >> text >> offset

            try:
                # Python v3.
                text = str(text, encoding='latin1')
            except TypeError:
                # Python v2.
                text = str(text)

            newLabel = DragLabel(text, self)
            newLabel.move(event.pos() - offset)
            newLabel.show()

            # crafting logic
            self.processDrop(newLabel, event.proposedAction()) 

            event.acceptProposedAction()

##            if event.source() in self.children():
##                event.setDropAction(Qt.MoveAction)
##                event.accept()
##            else:
##                event.acceptProposedAction()
        elif event.mimeData().hasText():
            pieces = event.mimeData().text().split()
            position = event.pos()

            for piece in pieces:
                newLabel = DragLabel(piece, self)
                newLabel.move(position)
                newLabel.show()

                position += QPoint(newLabel.width(), 0)

            event.acceptProposedAction()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if not child:
            return

        if child is self.result or child is self.countDisplay:
            return

        # store location of drag start
        self.startLocation = self.getLocation(self.mapFromGlobal(QCursor().pos()))
##        print(self.startLocation)

        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << QByteArray(child.labelText) << QPoint(event.pos() - child.pos())

        mimeData = QMimeData()
        mimeData.setData('application/x-fridgemagnet', itemData)
        mimeData.setText(child.labelText)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - child.pos())
        drag.setPixmap(child.pixmap())

        child.hide()

        if drag.exec_(Qt.MoveAction | Qt.CopyAction, Qt.MoveAction) == Qt.MoveAction:
            child.close()
        else:
            child.show()
        
    # returns index of location on widget
    # 0 => ingredients section, 1 => craft slot 1, 2 => craft slot 2, 3=> craft result
    def getLocation(self, coords):
        # ingredients
        if coords.y() >= self.height()/3:
            return 0
        # slots / result
        elif self.height()/12 <= coords.y() and coords.y() <= self.height()/4:
            # slot 1
            if self.width()*3/18 <= coords.x() and coords.x() <= self.width()*5/18:               
                return 1
            # slot 2
            elif self.width()*7/18 <= coords.x() and coords.x() <= self.width()*9/18:
                return 2
            # result
            elif self.width()*12/18 <= coords.x() and coords.x() <= self.width()*14/18:
                return 3
        # everything else
        return -1

    # determines what action to take depending where drag started and ended
    def setAction(self, event, startLoc, endLoc):
        # cannot put object into result or invalid areas
        if startLoc < 0:
            event.ignore()
            return
        
        # the only copy condition: ingredients to slots
        if startLoc is 0 and (endLoc is 1 or endLoc is 2):
            event.setDropAction(Qt.CopyAction)
            event.accept()
            return
        
        # the only move condition: slot to anywhere (if invalid, will remove ingredient from slot)
        if (startLoc is 1 or startLoc is 2):
            event.setDropAction(Qt.MoveAction)
            event.accept()
            return

        event.ignore()
        return

    # logic that checks whether to craft and whether craft is successful
    def processDrop(self, label, action):
##        print(self.startLocation, self.endLocation, action)

        # ingredient put onto a slot
        if self.endLocation is 1 or self.endLocation is 2:
            # slot 1
            if self.endLocation is 1:
                # remove existing ingredient in slot
                if self.slot1 is not None:
                    self.slot1.close()
                # refresh other slot and result if starting a new formula
                if (self.result is not None) or (action == Qt.MoveAction):
                    if self.result is not None:
                        self.result.close()
                        self.result = None
                    if self.slot2 is not None:
                        self.slot2.close()
                        self.slot2 = None
                # save label so we can access/destroy it later
                self.slot1 = label
                self.centerLabel(label, self.width()*4/18, self.height()*2/12)
            # slot 2
            else:
                # remove existing ingredient in slot
                if self.slot2 is not None:
                    self.slot2.close()
                # refresh other slot and result if starting a new formula
                if (self.result is not None) or (action == Qt.MoveAction):
                    if self.result is not None:
                        self.result.close()
                        self.result = None
                    if self.slot1 is not None:
                        self.slot1.close()
                        self.slot1 = None
                # save label so we can access/destroy it later
                self.slot2 = label
                self.centerLabel(label, self.width()*8/18, self.height()*2/12)

            # craft something if both slots are now filled
            if self.slot1 is not None and self.slot2 is not None:
                # check if formula is valid
                formula = self.slot1.labelText+"+"+self.slot2.labelText
                if formula in self.recipe:
                    resultLabel = self.recipe[formula]
                    # show result
                    self.result = DragLabel(resultLabel.labelText, self)
                    self.result.show()
                    self.centerLabel(self.result, self.width()*13/18, self.height()*2/12)
                    # check if result is new
                    if not resultLabel.isVisible():
                        self.count += 1
                        # update count display
                        self.countDisplay.close()
                        self.countDisplay = QLabel(str(self.count) + "/" + str(self.total), self)
                        self.countDisplay.show()
                        self.countDisplay.setAttribute(Qt.WA_DeleteOnClose)
                        self.centerLabel(self.countDisplay, self.width()/2, self.height()*5/6)
                        # show result as a new ingredient
                        resultLabel.show()
                # invalid formula
                else:
                    self.result = QLabel("Invalid", self)
                    self.result.show()
                    self.result.setAttribute(Qt.WA_DeleteOnClose)
                    self.centerLabel(self.result, self.width()*13/18, self.height()*2/12)

        # invalid move, destroy new and old label
        elif self.startLocation is 1:
            label.close()
            self.slot1.close()
            self.slot1 = None
        elif self.startLocation is 2:
            label.close()
            self.slot2.close()
            self.slot2 = None

    # center labels
    def centerLabel(self, label, center_x, center_y):
        label.move(center_x - label.width() / 2, center_y - label.height() / 2)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = DragWidget()
    window.show()    
    
    sys.exit(app.exec_())
