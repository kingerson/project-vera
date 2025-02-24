# %%
import locale
from datetime import datetime
from pathlib import Path

from exchangelib import Account, Credentials, FileAttachment, Mailbox, Message
from pandas import ExcelWriter

from general_tools import read_credentials, custom_timer, json_reader
import lector_datos

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')
# %%


def email_login():
    """Ingresa al correo y devuelve un objecto Account"""
    creds = read_credentials('correo_sb')
    email = creds['email']
    password = creds['password']
    credentials = Credentials(email, password)
    account = Account(email, credentials=credentials, autodiscover=True)
    return account


def creates_message(conn, tipo):
    """Crea el correo a ser envíado"""
    mensajes = {
        'por_vencer': Message(
            account=conn,
            subject='Casos Reclamaciones / IF a Vencer',
            body=(
                'Buenos días, equipo. Adjuntos los casos de reclamaciones e'
                ' información financiera que se han'
                f' tomado más de 30 días en ser concluídos. Información actualizada al {HOY_STRING}'
            ),
            to_recipients=[Mailbox(email_address=RECIPIENTS)],
            cc_recipients=CC_RECIPIENTS
        )
    }
    return mensajes[tipo]


def reads_data(file):
    """Lee el archivo de Excel a ser enviado en el correo"""
    with open(file, 'rb') as f:
        content = f.read()
    return content


def attach_file(msg, content, file):
    """Adjunta el archivo de Excel"""
    msg.attach(FileAttachment(
        name=file, content=content)
        )
    return msg


def sends_message(file, message_type):
    """Envía el mensaje a los destinatarios"""
    conn = email_login()
    msg = creates_message(conn, message_type)
    content = reads_data(file)
    msg = attach_file(msg, content, file)
    msg.send()
# %%


@custom_timer
def main():
    print('inicio')
    param_path = (Path(__file__).parent.parent / 'dicts/odata_parameters.json').as_posix()
    print(param_path)
    parameters = json_reader(param_path)['notificaciones']
    info = lector_datos.main(parameters['infofinanciera'])
    reclamos = lector_datos.main(parameters['reclamos'])
    print('Leyo data')
    print(info.head())
    with ExcelWriter(RESULT_FILENAME) as writer:
        info.to_excel(writer, sheet_name=INFO_SHEET_NAME, index=False)
        reclamos.to_excel(writer, sheet_name=RECLAMACIONES_SHEET_NAME, index=False)
    print('salvo archivo')
    print('creando mensajes')
    # Mensaje para Alexa
    sends_message(RESULT_FILENAME, 'por_vencer')
    print('envio correo por vencer')
    print('termino')
# %%


HOY_STRING = datetime.today().strftime('%d de %B de %Y')
BASE_PATH = (Path(__file__).resolve().parent.parent.parent / "Envios Notificaciones").as_posix()
INFO_SHEET_NAME = 'infofinanciera_a_vencer'
RECLAMACIONES_SHEET_NAME = 'reclamaciones_a_vencer'
RESULT_FILENAME = BASE_PATH + f'/procesos_a_vencer {HOY_STRING}.xlsx'
# RECIPIENTS = 'jacevedo@sb.gob.do'
RECIPIENTS = 'amarte@sb.gob.do'
CC_RECIPIENTS = ['adiaz@sb.gob.do', 'aluciano@sb.gob.do', 'drodriguez@sb.gob.do']

# %%
main()
