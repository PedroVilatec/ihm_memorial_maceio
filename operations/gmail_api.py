import base64
import dominate
import httplib2
import oauth2client
import os

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apiclient import discovery, errors
from dominate.tags import *
from oauth2client import client, tools

from instance.config import Config
from instance.message import Message


class GmailAPI():
    credential_dir = Config.CREDENTIALS_DIR
    scopes = Config.GMAIL_SCOPES
    gmailUserAuth = Config.GMAIL_USER_AUTH
    gmailServiceAuth = os.path.join(Config.CREDENTIALS_DIR, Config.GMAIL_SERVICE_AUTH)

    def __init__(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)

    def send_report(self, emails, date, header, content):
        sender = Config.EMAIL
        subject = Message.EMAIL_SUBJECT_REPORT % date
        message = self.create_report(sender, emails, subject, date, header, content)
        try:
            message = (self.service.users().messages().send(userId=sender, body=message)
                       .execute())
            print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def send_alert(self, emails, sensor_name, sensor_value, ideal_value):
        sender = Config.EMAIL
        subject = Message.EMAIL_SUBJECT_ALERT % sensor_name
        message = self.create_alert(sender, emails, subject, sensor_name, sensor_value, ideal_value)
        try:
            message = (self.service.users().messages().send(userId=sender, body=message)
                       .execute())
            print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def get_credentials(self):
        if not os.path.exists(self.credential_dir):
            os.makedirs(self.credential_dir)
        credential_path = os.path.join(self.credential_dir, self.gmailUserAuth)

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.gmailServiceAuth, self.scopes)
            credentials = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def create_report(self, sender, to, subject, date, header, content):
        message = MIMEMultipart('related')
        message['from'] = sender
        message['to'] = to
        message['subject'] = subject

        body = MIMEMultipart('alternative')
        message.attach(body)

        html = self.html_email_report(date, header, content)

        format_html = MIMEText(html.__str__(), 'html')

        body.attach(format_html)

        with open(os.path.join(Config.STATIC_DIR, 'LOGO_CEM.png'), 'rb') as file_content:
            content = MIMEImage(file_content.read())
        content.add_header('Content-ID', '<image1>')
        message.attach(content)

        with open(os.path.join(Config.STATIC_DIR, 'LOGO_VILATEC.png'), 'rb') as file_content:
            content = MIMEImage(file_content.read())
        content.add_header('Content-ID', '<image2>')
        message.attach(content)

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def create_alert(self, sender, to, subject, sensor_name, sensor_value, ideal_value):
        message = MIMEMultipart('related')
        message['from'] = sender
        message['to'] = to
        message['subject'] = subject

        body = MIMEMultipart('alternative')
        message.attach(body)

        html = self.html_email_alert(sensor_name, sensor_value, ideal_value)

        format_html = MIMEText(html.__str__(), 'html')

        body.attach(format_html)

        with open(os.path.join(Config.STATIC_DIR, 'LOGO_CEM.png'), 'rb') as file_content:
            content = MIMEImage(file_content.read())
        content.add_header('Content-ID', '<image1>')
        message.attach(content)

        with open(os.path.join(Config.STATIC_DIR, 'LOGO_VILATEC.png'), 'rb') as file_content:
            content = MIMEImage(file_content.read())
        content.add_header('Content-ID', '<image2>')
        message.attach(content)

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def html_email_alert(self, sensor_name, sensor_value, ideal_value):
        title = Config.SHEET
        doc = dominate.document(title=title)

        with doc:
            with div(style="display: table;"):
                with div(style="display: table-cell; vertical-align: middle;"):
                    img(src="cid:image1", style="float: left;", hspace="13px", height="75")
                    h1(title, style="display: table-cell; height: 75px; vertical-align: middle;")

                with div(style="display: table-row;"):
                    with div(style="display: table-cell;"):
                        with p(style="padding: 2px; text-align: left"):
                            h2("Atencao! O sensor de %s esta fora do valor ideal!" % (sensor_name))
                            p("Valor coletado: % s" % sensor_value, style="color:red")
                            p("Valor ideal: % s" % ideal_value)

                with div(style="display: table-row; text-align: center;"):
                    img(src="cid:image2", height="30")

        return doc

    def html_email_report(self, date, table_header, table_content):
        title = Config.SHEET
        doc = dominate.document(title=title)
        troca, teste = self.operations_count(table_content)

        with doc:
            with div(style="display: table;"):
                with div(style="display: table-cell; vertical-align: middle;"):
                    img(src="cid:image1", style="float: left;", hspace="13px", height="75")
                    h1(title, style="display: table-cell; height: 75px; vertical-align: middle;")

                with div(style="display: table-row;"):
                    with div(style="display: table-cell;"):
                        with p(style="padding: 2px; text-align: left"):
                            h2("Relatorio diario de operações - %s" % (date))
                            p("Total de trocas gasosas: %s" % troca)
                            p("Total de testes de estanqueidade: %s" % teste)

                with div(style="display: table-row;"):
                    h2("Historico:")

                    if table_header == [] or table_content == []:
                        p("Sem registros")
                    else:
                        with table().add(tbody()):
                            header = tr()
                            for title in table_header:
                                header.add(td(title))
                            for i in range(len(table_content)):
                                content = tr()
                                for value in table_content[i]:
                                    content.add(td(value))
                    br()

                with div(style="display: table-row; text-align: center;"):
                    img(src="cid:image2", height="30")

        return doc

    def operations_count(self, content):
        troca = 0
        teste = 0
        for row in content:
            if "TROCA" in row:
                troca += 1
            else:
                teste += 1
        return troca, teste
