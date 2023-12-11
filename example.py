import sys
import sqlite3
from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QPushButton, QPlainTextEdit
from PyQt5.QtGui import QFont
from errors import *

con = sqlite3.connect("design.sqlite")
cur = con.cursor()

app = QApplication(sys.argv)


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        desktop = app.desktop()
        self.setWindowTitle('GridMaster')
        x, y = desktop.availableGeometry().width(),\
               desktop.availableGeometry().height()
        self.setGeometry(0, 0, x, y)
        self.setStyleSheet('background-color : #252422;')

        self.codeplace = QPlainTextEdit(self)
        self.codeplace.setGeometry(50, 50, x - y - 50, (y - 150) // 3 * 2)
        self.codeplace.setFont(QFont('Arial', 30))
        self.codeplace.setStyleSheet('background-color : #2b2c28;'
                                     'color : white;'
                                     'border-radius: 10px;')

        self.errorplace = QPlainTextEdit(self)
        self.errorplace.setGeometry(50, (y - 150) // 3 * 2 + 100, x - y - 50,
                                   y - (y - 150) // 3 * 2 - 200)
        self.errorplace.setFont(QFont('Arial', 30))
        self.errorplace.setStyleSheet('background-color : #2b2c28;'
                                      'color : white;'
                                      'border-radius: 10px;')
        self.errorplace.setReadOnly(True)

        self.runcode = QPushButton(self)
        self.runcode.setGeometry(50, 0, 50, 50)
        self.runcode.setStyleSheet('background-color : green;')
        self.runcode.clicked.connect(self.code)

        self.returnstart = QPushButton(self)
        self.returnstart.setGeometry(100, 0, 50, 50)
        self.returnstart.setStyleSheet('background-color : blue;')
        self.returnstart.clicked.connect(self.returntostart)

        self.matrix = {}
        self.tilenum = {}
        for i in range(21):
            for j in range(21):
                tile = QPushButton(self)
                tile.setGeometry(x - y + 50 + ((x - y + 50) // 21) * i,
                                 50 + ((x - y + 50) // 21) * j,
                                 (x - y + 50) // 21, (x - y + 50) // 21)
                tile.setStyleSheet('background-color : gray;')
                self.matrix[(i, j)] = [i, j, 0, tile]
                self.tilenum[tile] = (i, j)
                tile.clicked.connect(self.setborder)
        self.matrix[list(self.matrix.keys())[0]][2] = 2
        self.matrix[list(self.matrix.keys())[0]][3].setStyleSheet(
            'background-color : red;')

        self.nowbot = (0, 0)

    def setborder(self):
        if self.matrix[self.tilenum[self.sender()]][2] == 0:
            self.sender().setStyleSheet('background-color : black;')
            self.matrix[self.tilenum[self.sender()]][2] = 1
        elif self.matrix[self.tilenum[self.sender()]][2] == 1:
            self.sender().setStyleSheet('background-color : gray;')
            self.matrix[self.tilenum[self.sender()]][2] = 0

    def code(self):
        self.errorplace.setPlainText('')
        s = self.codeplace.toPlainText()
        pohui = {}
        pohui2 = {}
        dointer = 0
        lastif = []
        notfunc = True
        self.nowbot = self.interpritator(s, pohui, pohui2,
                                         self.nowbot, dointer, lastif, notfunc)

    def returntostart(self):
        self.matrix[self.nowbot][2] = 0
        self.matrix[self.nowbot][3].setStyleSheet(
            'background-color : gray;')
        self.nowbot = (0, 0)
        self.matrix[self.nowbot][2] = 2
        self.matrix[self.nowbot][3].setStyleSheet(
            'background-color : red;')

    def interpritator(self,
                      s, pohui, pohui2, nowbot, dointer, lastif, notfunc):
        self.openif = 0
        self.openrep = 0
        self.openproc = 0

        self.v = 0
        for j, i in enumerate(s.split('\n')):
            try:
                result = self.inter(s, i, j, pohui, pohui2,
                                   nowbot, dointer, lastif, notfunc)
                if result:
                    self.matrix[nowbot][2] = 0
                    self.matrix[nowbot][3].setStyleSheet(
                        'background-color : gray;')
                    pohui = result[0]
                    pohui2 = result[1]
                    nowbot = result[2]
                    dointer = result[3]
                    lastif = result[4]
                    notfunc = result[5]
                    self.matrix[nowbot][2] = 2
                    self.matrix[nowbot][3].setStyleSheet(
                        'background-color : red;')
            except BorderError as ex:
                self.printexception(ex, j + 1)
                break
            except ParamError as ex:
                self.printexception(ex, j + 1)
                break
            except VoidError as ex:
                self.printexception(ex, j + 1)
                break
            except CodeError as ex:
                self.printexception(ex, j + 1)
                break
            except Exception as ex:
                print(ex)

        try:
            if self.openif != 0:
                raise CodeError('Незаконченная или неначатая команда IFBLOCK')
            elif self.openrep != 0:
                raise CodeError('Незаконченная или неначатая команда REPEAT')
            elif self.openproc != 0:
                raise CodeError('Незаконченная или неначатая команда'
                                ' PROCEDURE')
        except CodeError as ex:
            self.errorplace.setPlainText(f'Code:\n'
                                         f'{ex}')

        return nowbot

    def inter(self, s, i, j, pohui, pohui2, nowbot, dointer, lastif, notfunc):
        if not i:
            return pohui, pohui2, nowbot, dointer, lastif, notfunc
        cstr = i.split()
        if len(cstr) == 1:
            command = cstr[0]
            params = []
        else:
            command = cstr[0]
            params = cstr[1:]

        if command == 'IFBLOCK':
            self.v += 1
            self.openif += 1
        elif command == 'ENDIF':
            self.v -= 1
            self.openif -= 1
        elif command == 'REPEAT':
            self.v += 1
            self.openrep += 1
        elif command == 'ENDREPEAT':
            self.v -= 1
            self.openrep -= 1
        elif command == 'PROCEDURE':
            self.v += 1
            self.openproc += 1
        elif command == 'ENDPROC':
            self.v -= 1
            self.openproc -= 1

        if notfunc:
            if dointer == 0 and command == 'UP':
                if len(params) == 1:
                    if params[0] in pohui.keys():
                        params[0] = str(pohui[params[0]])
                    if params[0].isdigit():
                        sdv = int(params[0])
                        try:
                            for i in range(nowbot[1] - 1,
                                           nowbot[1] - sdv - 1, -1):
                                if self.matrix[(nowbot[0], i)][2] == 0:
                                    pass
                                else:
                                    raise BorderError(
                                        'Объект врезался в барьер')
                        except KeyError:
                            raise VoidError('Объект вышел за пределы поля')
                        nowbot = (nowbot[0], nowbot[1] - sdv)
                    else:
                        raise ParamError('Параметр не является числом')
                elif len(params) > 1:
                    raise ParamError('Указан(ы) непредвиденные параметры')
                else:
                    raise ParamError('Не указан параметр количества клеток')
            elif dointer == 0 and command == 'DOWN':
                if len(params) == 1:
                    if params[0] in pohui.keys():
                        params[0] = str(pohui[params[0]])
                    if params[0].isdigit():
                        sdv = int(params[0])
                        try:
                            for i in range(nowbot[1] + 1,
                                           nowbot[1] + sdv + 1):
                                if self.matrix[(nowbot[0], i)][2] == 0:
                                    pass
                                else:
                                    raise BorderError(
                                        'Объект врезался в барьер')
                        except KeyError:
                            raise VoidError('Объект вышел за пределы поля')
                        nowbot = (nowbot[0], nowbot[1] + sdv)
                    else:
                        raise ParamError('Параметр не является числом')
                elif len(params) > 1:
                    raise ParamError('Указан(ы) непредвиденные параметры')
                else:
                    raise ParamError('Не указан параметр количества клеток')
            elif dointer == 0 and command == 'RIGHT':
                if len(params) == 1:
                    if params[0] in pohui.keys():
                        params[0] = str(pohui[params[0]])
                    if params[0].isdigit():
                        sdv = int(params[0])
                        try:
                            for i in range(nowbot[0] + 1,
                                           nowbot[0] + sdv + 1):
                                if self.matrix[(i, nowbot[1])][2] == 0:
                                    pass
                                else:
                                    raise BorderError(
                                        'Объект врезался в барьер')
                        except KeyError:
                            raise VoidError('Объект вышел за пределы поля')
                        nowbot = (nowbot[0] + sdv, nowbot[1])
                    else:
                        raise ParamError('Параметр не является числом')
                elif len(params) > 1:
                    raise ParamError('Указан(ы) непредвиденные параметры')
                else:
                    raise ParamError('Не указан параметр количества клеток')
            elif dointer == 0 and command == 'LEFT':
                if len(params) == 1:
                    if params[0] in pohui.keys():
                        params[0] = str(pohui[params[0]])
                    if params[0].isdigit():
                        sdv = int(params[0])
                        try:
                            for i in range(nowbot[0] - 1,
                                           nowbot[0] - sdv - 1, -1):
                                if self.matrix[(i, nowbot[1])][2] == 0:
                                    pass
                                else:
                                    raise BorderError(
                                        'Объект врезался в барьер')
                        except KeyError:
                            raise VoidError('Объект вышел за пределы поля')
                        nowbot = (nowbot[0] - sdv, nowbot[1])
                    else:
                        raise ParamError('Параметр не является числом')
                elif len(params) > 1:
                    raise ParamError('Указан(ы) непредвиденные параметры')
                else:
                    raise ParamError('Не указан параметр количества клеток')
            elif command == 'IFBLOCK':
                if len(params) == 1:
                    try:
                        if params[0] == 'RIGHT':
                            if self.matrix[(nowbot[0] + 1, nowbot[1])][2] == 0:
                                dointer += 1
                                lastif.append(False)
                            else:
                                lastif.append(True)
                        elif params[0] == 'LEFT':
                            if self.matrix[(nowbot[0] - 1, nowbot[1])][2] == 0:
                                dointer += 1
                                lastif.append(False)
                            else:
                                lastif.append(True)
                        elif params[0] == 'UP':
                            if self.matrix[(nowbot[0], nowbot[1] - 1)][2] == 0:
                                dointer += 1
                                lastif.append(False)
                            else:
                                lastif.append(True)
                        elif params[0] == 'DOWN':
                            if self.matrix[(nowbot[0], nowbot[1] + 1)][2] == 0:
                                dointer += 1
                                lastif.append(False)
                            else:
                                lastif.append(True)
                        else:
                            raise ParamError(
                                'Неправильный параметр направления')
                    except KeyError:
                        dointer += 1
                        lastif.append(False)
                elif len(params) > 1:
                    raise ParamError('Указан(ы) непредвиденные параметры')
                else:
                    raise ParamError('Не указан параметр проверки')
            elif command == 'ENDIF':
                if not lastif[-1]:
                    dointer -= 1
                del lastif[-1]
            elif command == 'REPEAT':
                if len(params) == 1:
                    if params[0] in pohui.keys():
                        params[0] = str(pohui[params[0]])
                    if params[0].isdigit():
                        sdv = int(params[0])
                        if sdv != 0:
                            start = j + 1
                            end = j + 1
                            countrepeats = 1
                            while countrepeats != 0:
                                if s.split('\n')[end].split()[0] == 'REPEAT':
                                    countrepeats += 1
                                elif s.split('\n')[end] == 'ENDREPEAT':
                                    countrepeats -= 1
                                end += 1
                            for _ in range(sdv - 1):
                                for j2 in range(start, end):
                                    i2 = s.split('\n')[j2]
                                    result = self.inter(s, i2, j2, pohui,
                                                        pohui2, nowbot,
                                                        dointer, lastif,
                                                        notfunc)
                                    if result:
                                        self.matrix[nowbot][2] = 0
                                        self.matrix[nowbot][3].setStyleSheet(
                                            'background-color : gray;')
                                        pohui = result[0]
                                        pohui2 = result[1]
                                        nowbot = result[2]
                                        dointer = result[3]
                                        lastif = result[4]
                                        notfunc = result[5]
                                        self.matrix[nowbot][2] = 2
                                        self.matrix[nowbot][3].setStyleSheet(
                                            'background-color : red;')
                                print('Закончилось', _ + 1, start, end)
                            print('Повторение', 'last', start, end)
                        else:
                            raise ParamError('Количество повторений не должно '
                                             'быть равно нулю')
                    else:
                        raise ParamError('Параметр не является числом')
                elif len(params) > 1:
                    raise ParamError('Указан(ы) непредвиденные параметры')
                else:
                    raise ParamError(
                        'Не указан параметр количества повторений')
            elif command == 'ENDREPEAT':
                pass
            elif command == 'SET':
                if len(params) == 3 and params[1] == '=':
                    if params[0].isdigit():
                        raise ParamError('Нельзя назвать переменную числом')
                    else:
                        if params[2].isdigit():
                            pohui[params[0]] = int(params[2])
                        else:
                            raise ParamError(
                                'Переменная должна быть числом')
                else:
                    raise ParamError('Неверно задана переменная')
            elif command == 'PROCEDURE':
                if len(params) == 1:
                    if params[0].isdigit():
                        raise ParamError('Нельзя назвать функцию числом')
                    else:
                        j2 = j + 1
                        while s.split('\n')[j2].split()[0] != 'ENDPROC':
                            j2 += 1
                        pohui2[params[0]] = [j + 1, j2]
                        notfunc = False
                elif len(params) > 1:
                    raise ParamError('Указан(ы) непредвиденные параметры')
                else:
                    raise ParamError('Не указан параметр названия функции')
            elif command == 'CALL':
                if len(params) == 1:
                    if params[0] not in pohui2:
                        raise ParamError('Несуществующая функция')
                    else:
                        for j2 in range(pohui2[i.split()[1]][0],
                                        pohui2[i.split()[1]][1]):
                            i2 = s.split('\n')[j2]
                            self.v += 1
                            if self.v > 3:
                                raise CodeError('Ограничение по вложенности 3')
                            result = self.inter(s, i2, j2, pohui,
                                                pohui2, nowbot,
                                                dointer, lastif,
                                                notfunc)
                            self.v -= 1
                            if result:
                                self.matrix[nowbot][2] = 0
                                self.matrix[nowbot][3].setStyleSheet(
                                    'background-color : gray;')
                                pohui = result[0]
                                pohui2 = result[1]
                                nowbot = result[2]
                                dointer = result[3]
                                lastif = result[4]
                                notfunc = result[5]
                                self.matrix[nowbot][2] = 2
                                self.matrix[nowbot][3].setStyleSheet(
                                    'background-color : red;')
                elif len(params) > 1:
                    raise ParamError('Указан(ы) непредвиденные параметры')
                else:
                    raise ParamError('Не указан параметр названия функции')
            else:
                raise CodeError('Несуществующая команда')
        elif command == 'ENDPROC':
            if i != 'ENDPROC':
                raise ParamError('Лишние параметры')
            else:
                notfunc = True
        return pohui, pohui2, nowbot, dointer, lastif, notfunc

    def printexception(self, exc, num):
        self.errorplace.setPlainText(f'Line {num}:\n'
                                     f'{exc}')
