import iso8601
import pygsheets
import os

from datetime import *

from infra.lib_sensors_db import *
from operations import Message
from operations import Config


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Sheet(metaclass=Singleton):
    cells_ideal_values = []
    cells_intervalo = []
    sheetAuth = os.path.join(Config.CREDENTIALS_DIR, Config.SHEET_AUTH)

    def __init__(self):
        self.client = pygsheets.authorize(service_file=self.sheetAuth)

        self.createSheet()
        #print(self.client.spreadsheet_ids())
        #self.client.delete(Config.SHEET)
        self.wksControl = self.sheet.worksheet_by_title(Config.WORKSHEET_TAB1)
        self.wksData = self.sheet.worksheet_by_title(Config.WORKSHEET_TAB2)
        self.wksBody = self.sheet.worksheet_by_title(Config.WORKSHEET_TAB3)
        self.updateName(Config.SHEET)

    def updateData(self, operation, time, values, timeNow=None):
        if timeNow is None:
            timeNow = datetime.now().strftime('%X')
        data = [operation.upper(), time.weekDay.name, time.calendarDate,
                time.hour, timeNow]
        self.wksData.insert_rows(Config.INSERT_ROW, values=(data + values))

    def createSheet(self):
        try:
            self.sheet = self.client.open(Config.SHEET)
            print(self.sheet)
        except pygsheets.SpreadsheetNotFound:
            print(Message.SHEET_NOT_FOUND + Config.SHEET)
            print(Message.SHEET_CREATE + Config.SHEET)
            self.sheet = self.client.create(Config.SHEET)
            self.cloneSheetModel()
            self.shareSheet(Config.EMAIL)

    def cloneSheetModel(self):
        sheetModel = self.client.open(Config.SHEET_MODEL)
        sheetModelID = sheetModel.id
        sheetModelWorksheets = sheetModel.worksheets()
        for worksheet in sheetModelWorksheets:
            if self.existWorksheet(worksheet.title):
                print(Message.WORKSHEET_EXIST + worksheet.title)
            else:
                print(Message.WORKSHEET_COPY + worksheet.title
                      + Message.WORKSHEET_COPY_TO + self.sheet.title)
                self.sheet.add_worksheet(worksheet.title, src_tuple=(sheetModelID, worksheet.id))
        print(Message.WORKSHEET_DELETE_SHEET1)
        self.sheet.del_worksheet(self.sheet.sheet1)

    def existWorksheet(self, title):
        sheetWorksheets = self.sheet.worksheets()
        for worksheet in sheetWorksheets:
            if title == worksheet.title:
                return True
        return False

    def getAllRecords(self, string_date):
        num_cols = self.wksData.cols
        filter_records = self.wksData.find(string_date)
        if filter_records != []:
            frist_record_row = filter_records[0].row
            last_record_row = filter_records[-1].row
            start_cell = (frist_record_row, 1)
            end_cell = (last_record_row, num_cols)
            header = self.wksData.get_row(2)
            matrix_records = self.wksData.get_values(start=start_cell, end=end_cell, include_empty=False)
        else:
            header, matrix_records = [], []
        return header, matrix_records

    def getCellsParameters(self):
        sensors_name = get_sensors_type()
        if len(self.cells_ideal_values) == 0 or len(self.cells_intervalo) == 0:
            for sensor in sensors_name:
                cell = self.wksControl.find(sensor)[0]
                row, col = cell.row, cell.col
                self.cells_ideal_values.append((sensor, (row + 1, col)))
                self.cells_intervalo.append((sensor, (row + 2, col)))
        return self.cells_ideal_values, self.cells_intervalo

    def setValuesParameters(self):
        sensors_info = get_sensors_info()
        ideal_values, intervalo = self.getCellsParameters()
        len_cells, len_intervalo = len(ideal_values), len(intervalo)
        if len_cells == len_intervalo:
            for info in sensors_info:
                name = info[0]
                for i in range(len_cells):
                    if name == ideal_values[i][0] or name == intervalo[i][0]:
                        self.wksControl.update_cell(ideal_values[i][1], info[1])
                        self.wksControl.update_cell(intervalo[i][1], info[2])
        else:
            print("set param values - list out of range")

    def deleteValueParameter(self, nome_sensor):
        ideal_values, intervalo = self.getCellsParameters()
        len_cells, len_intervalo = len(ideal_values), len(intervalo)
        if len_cells == len_intervalo:
            name = nome_sensor
            for i in range(len_cells):
                if name == ideal_values[i][0] or name == intervalo[i][0]:
                    self.wksControl.update_cell(ideal_values[i][1], '')
                    self.wksControl.update_cell(intervalo[i][1], '')
        else:
            print("set param values - list out of range")

    def op_sheet_body(self, operation=None, id=None, values=None):
        if operation == 'add':
            self.updateListBody(values)
        elif operation == 'update':
            self.updateBody(id, values)
        elif operation == 'del':
            self.deleteBody(id)


    def updateListBody(self, values):
        self.wksBody.insert_rows(Config.INSERT_ROW, values=values)

    def updateBody(self, ID, values):
        try:
            cell = self.wksBody.find(str(ID))
            row = cell[0].row
            self.wksBody.update_row(row, values)
        except IndexError:
            self.updateListBody(values)

    def deleteBody(self, ID):
        try:
            cell = self.wksBody.find(str(ID))
            row = cell[0].row
            self.wksBody.delete_rows(row)
        except Exception:
            print(Message.SHEET_BODY)

    def shareSheet(self, email):
        self.sheet.share(email, role='writer')

    def removeShare(self, email):
        self.sheet.remove_permissions(email)

    def updateName(self, name):
        self.wksControl.update_cell(Config.CELL_TITLE, name)

    def sheetUpated(self):
        return iso8601.parse_date(self.sheet.updated)

    def get_horario_troca(self):
        hours = []

        hour_first = self.wksControl.get_values(start=(2, 5), end=(2, 16), include_all=True)[0]
        minutes_first = self.wksControl.get_values(start=(3, 5), end=(3, 16), include_all=True)[0]
        first_exec = self.wksControl.get_values(start=(4, 5), end=(4, 16), include_all=True)[0]

        for i in range(len(hour_first)):
            if first_exec[i] != '':
                if minutes_first[i] == '':
                    minute = '00'
                else:
                    minute = minutes_first[i]
                msg = hour_first[i] + ":" + minute
                hours.append(msg)

        hour_second = self.wksControl.get_values(start=(5, 5), end=(5, 16), include_all=True)[0]
        minutes_second = self.wksControl.get_values(start=(6, 5), end=(6, 16), include_all=True)[0]
        second_exec = self.wksControl.get_values(start=(7, 5), end=(7, 16), include_all=True)[0]

        for i in range(len(hour_second)):
            if second_exec[i] != '':
                if minutes_second[i] == '':
                    minute = '00'
                else:
                    minute = minutes_second[i]
                hours.append(hour_second[i] + ":" + minute)

        return hours

    def get_horario_teste(self):
        hour = self.wksControl.get_value((3, 18))
        return hour
