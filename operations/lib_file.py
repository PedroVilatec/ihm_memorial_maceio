import ast
import os

from datetime import *

from operations import Config
from operations import Message


class LibFile():
    out_dir = Config.OUTPUT_DIR

    def __init__(self, fileName):
        self.fileName = fileName + Config.FILE_EXTENSION
        self.newLine = "\n"
        self.divider = Config.FILE_DIVIDER

    def existFile(self):
        try:
            if not os.path.exists(self.out_dir):
                os.makedirs(self.out_dir)
            file = open(os.path.join(self.out_dir, self.fileName), "x")
            file.close()
        except FileExistsError:
            print(Message.FILE_EXIST + self.fileName)

    def getItemId(self):
        try:
            with open(os.path.join(self.out_dir, self.fileName), 'r') as file:
                fileLines = file.readlines()
                lastLine = len(fileLines)
                id = int(fileLines[lastLine-1].split(self.divider)[0])
                return id + 1
        except IndexError:
            print(Message.FILE_EMPTY + self.fileName)
        return 1

    def formatListToString(self, arg):
        string = ''
        for element in arg:
            string += element.__str__() + self.divider
        string += self.newLine
        return string

    def updateFile(self, time, values):
        self.existFile()
        data = [self.getItemId(), time.weekDay.name, time.calendarDate, time.hour,
               datetime.now().strftime('%X')] + values
        with open(os.path.join(self.out_dir, self.fileName), "a") as file:
            file.write(self.formatListToString(data))

    def updateEmails(self, emails, date):
        self.existFile()
        data = [self.getItemId(), emails, date]
        with open(os.path.join(self.out_dir, self.fileName), "a") as file:
            file.write(self.formatListToString(data))

    def updateAlerts(self, emails, sensor_name, sensor_value, ideal_value):
        self.existFile()
        data = [self.getItemId(), emails, sensor_name, sensor_value, ideal_value]
        with open(os.path.join(self.out_dir, self.fileName), "a") as file:
            file.write(self.formatListToString(data))

    def formatStringToList(self, string):
        returnList = string.split(Config.FILE_DIVIDER)
        returnList[1] = self.fileName[:-4]
        returnList.remove(self.newLine)
        return returnList

    def formatStringEmailToList(self, string):
        returnList = string.split(Config.FILE_DIVIDER)
        returnList[1] = ast.literal_eval(returnList[1])
        returnList.remove(self.newLine)
        return returnList

    def getRecords(self):
        listLines = []
        with open(os.path.join(self.out_dir, self.fileName), "r") as file:
            lines = file.readlines()
            for line in lines:
                if '@' in line:
                    listLines.append(self.formatStringEmailToList(line))
                else:
                    listLines.append(self.formatStringToList(line))
        return listLines

    def delteRecord(self, id):
        records = self.getRecords()
        newRecords = []
        for record in records:
            if record[0] == str(id):
                pass
            else:
                newRecords.append(self.formatListToString(record))
        with open(os.path.join(self.out_dir, self.fileName), "w") as file:
            for record in newRecords:
                file.write(record)

