from datetime import datetime
from enum import Enum

from instance.config import Config
from instance.message import Message

from operations.lib_file import LibFile
from operations.send_email import SendEmail
from operations.sheet import Sheet

time = None


class weekDay(Enum):
    SEG = 0
    TER = 1
    QUA = 2
    QUI = 3
    SEX = 4
    SAB = 5
    DOM = 6


class Time:
    def __init__(self, time):
        self.weekDay = weekDay(time.weekday())
        self.calendarDate = time.strftime('%d/%m/%Y')
        self.hour = time.strftime('%T')


def alertEmail(emails, sensor_name, sensor_value, ideal_value, record=None):
    libFile = LibFile('email_alert')
    try:
        email = SendEmail(emails)
        if libFile.getItemId() is 1:
            print(Message.EMAIL_FILE_EMPTY)
            email.send_alert(sensor_name, sensor_value, ideal_value)
        elif record is None:
            print(Message.EMAIL_OLD_RECORDS)
            records = libFile.getRecords()
            for record in records:
                alertEmail(record[1], record[2], record[3], record[4], record[0])
            email.send_alert(sensor_name, sensor_value, ideal_value)
        else:
            print(Message.EMAIL_FILE_NOT_EMPTY)
            email.send_alert(sensor_name, sensor_value, ideal_value)
            print(Message.EMAIL_DELETE_RECORD + record)
            libFile.delteRecord(record)
    except:
        print(Message.EMAIL_WITHOUT_INTERNET)
        libFile.updateAlerts(emails, sensor_name, sensor_value, ideal_value)


def dailyEmail(emails, date, record=None):
    libFile = LibFile('email_report')
    try:
        sheet = Sheet()
        email = SendEmail(emails)
        table_header, table_content = sheet.getAllRecords(date)
        if libFile.getItemId() is 1:
            print(Message.EMAIL_FILE_EMPTY)
            email.send_report(date, table_header, table_content)
        elif record is None:
            print(Message.EMAIL_OLD_RECORDS)
            records = libFile.getRecords()
            for record in records:
                dailyEmail(record[1], record[2], record[0])
            email.send_report(date, table_header, table_content)
        else:
            print(Message.EMAIL_FILE_NOT_EMPTY)
            email.send_report(date, table_header, table_content)
            print(Message.EMAIL_DELETE_RECORD + record)
            libFile.delteRecord(record)
    except:
        print(Message.EMAIL_WITHOUT_INTERNET)
        libFile.updateEmails(emails, date)


def updateData(fileName, time, values, timeNow=None, record=None):
    libFile = LibFile(fileName)
    try:
        sheet = Sheet()
        if libFile.getItemId() is 1:
            print(Message.RECORD_FILE_EMPTY)
            sheet.updateData(fileName, time, values)
        elif record is None:
            print(Message.RECORD_OLD_RECORDS)
            records = libFile.getRecords()
            for record in records:
                fileName, time, timeNow, values = parseRecord(record)
                updateData(fileName, time, values, timeNow, record[0])
            sheet.updateData(fileName, time, values)
        else:
            print(Message.RECORD_FILE_NOT_EMPTY)
            sheet.updateData(fileName, time, values, timeNow)
            print(Message.RECORD_DELETE_RECORD + record)
            libFile.delteRecord(record)
    except:
        print(Message.RECORD_WITHOUT_INTERNET)
        libFile.updateFile(time, values)
"""
    def updateBody(operation, id = None, values = None, record=None):
        libFile = LibFile('body')
        try:
            sheet = Sheet()
            if libFile.getItemId() is 1:
                print(Message.RECORD_FILE_EMPTY)
                sheet.op_sheet_body(operation, id, values)
            elif record is None:
                print(Message.RECORD_OLD_RECORDS)
                records = libFile.getRecords()
                for record in records:
                    updateBody(operation, id = None, values = None, record=None)
                sheet.op_sheet_body(operation, id = None, values = None, record=None)
            else:
                print(Message.RECORD_FILE_NOT_EMPTY)
                sheet.op_sheet_body(operation, id = None, values = None, record=None)
                print(Message.RECORD_DELETE_RECORD + record)
                libFile.delteRecord(record)
        except:
            print(Message.RECORD_WITHOUT_INTERNET)
            libFile.updateFile(operation, id = None, values = None, record=None)
"""
def setTime():
    return Time(datetime.now())


def parseRecord(record):
    fileName = record[1]
    date, hour = record[2].split(Config.DATE_DIVIDER), record[3].split(Config.CLOCK_DIVIDER)
    date, hour = [int(x) for x in date], [int(x) for x in hour]
    time = Time(datetime(date[2], date[1], date[0], hour[0], hour[1], hour[2]))
    values = record[5:]
    timeNow = record[4]
    return fileName, time, timeNow, values