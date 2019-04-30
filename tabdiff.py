from pprint import pprint


class PyvotabElement(dict):

    def __init__(self, parent, isNew, sourceID):
        self.parent = parent
        self.dimension = 0
        self.sourceID = sourceID
        self.oldValue = 'NaN'
        self.newValue = 'NaN'
        # 0= old, 1= unchanged, 2 = new
        if not isNew:
            self.state = 0
        else:
            self.state = 2

    def increaseDimension(self):
        self.dimension += 1
        if self.parent:
            self.parent.increaseDimension()

    def validateState(self, isNew):
        if self.state == 1:  # signals old and new
            return
        # 0= old, 1= unchanged, 2 = new
        if not isNew:
            newState = 0
        else:
            newState = 2
        if self.state != newState:
            print("state change:", self.state, newState)
            self.state = 1  # marks

    def get_state(self):
        return self.state

    def add(self, value, isNew, sourceID):
        self.validateState(isNew)
        if self.sourceID == -1:  # it's one of the inital elements
            self.sourceID = sourceID
        self.increaseDimension()
        if not value in self:
            self[value] = PyvotabElement(self, isNew, sourceID)
            return self[value]
        else:
            self[value].validateState(isNew)
            return self[value]

    def MakeValue(self, value, rowDt, colDt, isNew):
        self.rowDt = rowDt
        self.colDt = colDt
        if isNew:
            self.newValue = value
            print("state change state from:", self.state, "for value ", value)
            if self.oldValue != value:
                self.state = 2
            else:
                self.state = 1
            print("state change state to:", self.state)
        else:
            self.oldValue = value

    def getEndPoint(self, myhash):
        try:
            return self[hash(myhash)]
        except:
            return None

    def setEndPoint(self, newEndPoint, myhash):
        self[hash(myhash)] = newEndPoint
        self.isEndStup = True

    def setPrintCoords(self, startCoord, level, xDirection):
        if xDirection:
            self.printY = startCoord
            print("set Y {0} for {1}".format(startCoord, self.oldValue))
        else:
            self.printX = startCoord
            print("set X {0} for {1}".format(startCoord, self.oldValue))

    def calPrintCoords(self, startCoord, level, xDirection):
        self.startCoord = startCoord
        self.blockSize = startCoord
        self.level = level
        isEnd = False
        try:
            self.isEndStup
            isEnd = True
        except:  # this is no endstup
            startCoord -= 1  # reduce it, so that the return value is the same as the start in case this element and its subs covers only 1 row/column

        for index in sorted(self.keys()):
            if isEnd:
                self[index].setPrintCoords(startCoord, level, xDirection)
            else:
                startCoord += 1
                startCoord = self[index].calPrintCoords(
                    startCoord, level+1, xDirection)
        self.blockSize = startCoord-self.blockSize+1
        return startCoord

    def depth(self, actLevel):
        resultLevel = actLevel
        for index in self:
            try:
                self[index].isEndStup
                return actLevel
            except:
                newLevel = self[index].depth(actLevel+1)
                if newLevel > resultLevel:
                    resultLevel = newLevel
        return resultLevel

    def fillPrintGridValue(self, multiplier, xDirection,  fillFunction):
        value = "'{0}|{1}' ({2})".format(
                self.oldValue, self.newValue, self.state)
        fillFunction(value, self.printX, self.printY,
                     xDirection, 1, self.sourceID)

    def fillPrintGrid(self, multiplier, xDirection, fillFunction, old_style):
        for index in sorted(self.keys()):
            isEnd = False
            try:
                self.isEndStup
                isEnd = True
            except:
                pass
            if isEnd:
                self[index].fillPrintGridValue(
                    multiplier, xDirection, fillFunction)
            else:
                # determine correct style based on, if the element is old or not
                if self[index] == 0:
                    this_style = old_style
                else:
                    this_style = self[index].sourceID
                value = "'{0}' ({1})".format(index, self[index].get_state())

                if xDirection:
                    fillFunction(
                        value, self.level, self[index].startCoord, xDirection, self.blockSize, this_style)
                else:
                    fillFunction(
                        value, self[index].startCoord, self.level, xDirection, self.blockSize, this_style)
                self[index].fillPrintGrid(
                    multiplier, xDirection, fillFunction, old_style)

    def pprint(self):
        if self:
            for key, value in self.items():
                print("{{'{0}'".format(hex(id(value))), end='')
                if value.state == 0:
                    print("-", end="")
                if value.state == 2:
                    print("+", end="")
                print(": ", end='')
                value.pprint()
                print('}} ', end='')
        else:
            print("<{0}|{1}> {2}".format(self.oldValue,
                                         self.newValue, self.state), end='')


class Pivotab:

    def __init__(self, firstSourceID):
        self.rowTd = PyvotabElement(None, False, -1)
        self.colTd = PyvotabElement(None, False, -1)
        self.old_style = firstSourceID

    def headerrows(self):
        return self.rowTd.depth(1)

    def headercols(self):
        return self.colTd.depth(1)

    def insertTable(self, table, splitPoint, state, sourceID):
        for row in table:
            rowWidth = len(row)
            actRowDt = self.rowTd
            actColDt = self.colTd
            rowHash = ""
            colHash = ""
            for key, val in enumerate(row):
                if key == rowWidth-1:
                    # remember: rows gets colhashes & vice versa
                    rowEndPoint = actRowDt.getEndPoint(colHash)
                    colEndPoint = actColDt.getEndPoint(rowHash)
                    if rowEndPoint == None and colEndPoint == None:
                        newEndPoint = PyvotabElement(None, state, sourceID)
                        actRowDt.setEndPoint(newEndPoint, colHash)
                        actColDt.setEndPoint(newEndPoint, rowHash)
                    else:
                        if rowEndPoint == None:
                            newEndPoint = colEndPoint
                            actRowDt.setEndPoint(newEndPoint, colHash)
                        else:
                            newEndPoint = rowEndPoint
                            actColDt.setEndPoint(newEndPoint, rowHash)

                    newEndPoint.MakeValue(
                        val, actRowDt, actColDt, state)
                else:
                    if key < splitPoint:
                        actRowDt = actRowDt.add(val, state, sourceID)
                        rowHash += ":"+val
                    else:
                        actColDt = actColDt.add(val, state, sourceID)
                        colHash += ":"+val

    def layoutGrid(self):
        self.rowTd.calPrintCoords(self.colTd.depth(1), 0, True)
        self.colTd.calPrintCoords(self.rowTd.depth(1), 0, False)

    def getPrintDict(self):
        self.ptdict = ptPrintDict()
        self.rowTd.fillPrintGrid(1, True, self.printfunction, self.old_style)
        self.colTd.fillPrintGrid(1, False, self.printfunction, self.old_style)
        return self.ptdict

    def printfunction(self, value, px, py, xDirection, blocksize, style):
        print("print:", value, px, py, xDirection, blocksize)
        try:
            self.ptdict[px]
        except:
            self.ptdict[px] = {}
        self.ptdict[px][py] = {
            "value": value, "style": style, "size": blocksize, "xDir": xDirection}
        print("gespeichert:", self.ptdict[px][py])
        if self.ptdict.xSize < px:
            self.ptdict.xSize = px
        if self.ptdict.ySize < py:
            self.ptdict.ySize = py


class ptPrintDict(dict):
    xSize = 0
    ySize = 0


t1 = [
    ['Hans', 'Mueller', 'Hamburg', 'Postweg', 8],
    ['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 5],
    ['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
    ['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
]

t2 = [
    ['Hins', 'Mueller', 'Hamburg', 'Postweg', 8],
    ['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 5],
    ['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
    ['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
    ['Klaus', 'Schulze', 'Berlin', 'am Deich', 9],
    ['Hans', 'Mueller', 'Berlin', 'am Deich', 10],
]

t3 = [
    ['Hans', 'Mueller', 'Hamburg', 'Postweg', 8]
]

t4 = [
    ['Hins', 'Mueller', 'Hamburg', 'Postweg', 8]
]

pt = Pivotab("grey")

pt.insertTable(t1, 2, False, "lightgrey")
pt.insertTable(t2, 2, True, "lightblue")


rowDepth = pt.headerrows()
colDepth = pt.headercols()
print("rowDepth", rowDepth)
print("colDepth", colDepth)
pt.layoutGrid()
printDict = pt.getPrintDict()
print("<table>")
for x in range(printDict.xSize+1):
    print("<tr>")
    for y in range(printDict.ySize+1):
        try:
            printDict[x][y]
        except:
            print("<td/> ", end='')
            continue
        print("<td ", end='')

        print('style="background-color:', end='')
        print(printDict[x][y]["style"]+'" ', end='')
        '''
		if printDict[x][y]["xDir"]:
			print('colspan="',end='')
		else:
			print('rowspan="',end='')
		print(str(printDict[x][y]["size"])+'" ',end='')
		'''
        print(">", end='')

        print(printDict[x][y]["value"]+"</td>", end='')
    print("</tr>")
print("</table>")
