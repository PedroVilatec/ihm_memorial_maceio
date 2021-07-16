from operations.gmail_api import GmailAPI


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SendEmail(metaclass=Singleton):
    def __init__(self, emails):
        self.emails = self.list_to_string(emails)
        self.gmail_api = GmailAPI()

    def list_to_string(self, emails):
        return ','.join(emails)

    def send_report(self, date, table_header, table_content):
        self.gmail_api.send_report(self.emails, date, table_header, table_content)

    def send_alert(self, sensor_name, sensor_value, ideal_value):
        lower_name = sensor_name.lower()
        self.gmail_api.send_alert(self.emails, lower_name, sensor_value, ideal_value)