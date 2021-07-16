class Message():
    FILE_EXIST = "libFile - file exist: "
    FILE_EMPTY = "libFile - empty file: "

    SHEET_NOT_FOUND = "libSheet - sheet not found: "
    SHEET_CREATE = "libSheet - create sheet: "
    SHEET_BODY = "body not found"

    WORKSHEET_EXIST = "libSheet - worksheet exist: "
    WORKSHEET_COPY = "libSheet - copy worksheet: "
    WORKSHEET_COPY_TO = " to: "
    WORKSHEET_DELETE_SHEET1 = "libSheet - delete sheet1"

    RECORD_FILE_EMPTY = "update record: file empty"
    RECORD_FILE_NOT_EMPTY = "update record: file not empty"
    RECORD_OLD_RECORDS = "update record: write old records"
    RECORD_DELETE_RECORD = "update record: delete record "
    RECORD_WITHOUT_INTERNET = "update record: without internet connection"

    EMAIL_FILE_EMPTY = "update emails record: file empty"
    EMAIL_FILE_NOT_EMPTY = "update emails record: file not empty"
    EMAIL_OLD_RECORDS = "update emails record: write old records"
    EMAIL_DELETE_RECORD = "update emails record: delete record "
    EMAIL_WITHOUT_INTERNET = "update emails record: without internet connection"

    EMAIL_SUBJECT_REPORT = 'Relatorio diario de operacoes - %s'
    EMAIL_SUBJECT_ALERT = "Atencao! Sensor de %s esta fora do valor ideal."
