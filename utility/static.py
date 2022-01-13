import sqlite3
import zipfile
import datetime
import telegram
import pandas as pd
from threading import Thread
from utility.setting import DB_STG, OPENAPI_PATH

connn = sqlite3.connect(DB_STG)
df_tg = pd.read_sql('SELECT * FROM telegram', connn)
connn.close()
if len(df_tg) > 0 and df_tg['str_bot'][0] != '':
    bot = df_tg['str_bot'][0]
    user_id = int(df_tg['int_id'][0])
else:
    bot = ''
    user_id = 0


def telegram_msg(text):
    if bot == '':
        print('텔레그램 봇이 설정되지 않아 메세지를 보낼 수 없습니다.')
    else:
        try:
            telegram.Bot(bot).sendMessage(chat_id=user_id, text=text)
        except Exception as e:
            print(f'텔레그램 설정 오류 알림 - telegram_msg {e}')


def thread_decorator(func):
    def wrapper(*args):
        Thread(target=func, args=args, daemon=True).start()
    return wrapper


def now():
    return datetime.datetime.now()


def timedelta_sec(second, std_time=None):
    if std_time is None:
        next_time = now() + datetime.timedelta(seconds=second)
    else:
        next_time = std_time + datetime.timedelta(seconds=second)
    return next_time


def timedelta_day(day, std_time=None):
    if std_time is None:
        next_time = now() + datetime.timedelta(days=day)
    else:
        next_time = std_time + datetime.timedelta(days=day)
    return next_time


def strp_time(timetype, str_time):
    return datetime.datetime.strptime(str_time, timetype)


def strf_time(timetype, std_time=None):
    if std_time is None:
        str_time = now().strftime(timetype)
    else:
        str_time = std_time.strftime(timetype)
    return str_time


def comma2int(t):
    if ' ' in t:
        t = t.split(' ')[1]
    if ',' in t:
        t = t.replace(',', '')
    return int(t)


def float2str3p2(t):
    t = str(t)
    if len(t.split('.')[0]) == 1:
        t = '  ' + t
    if len(t.split('.')[0]) == 2:
        t = ' ' + t
    if len(t.split('.')[1]) == 1:
        t += '0'
    return t


def float2str2p2(t):
    t = str(t)
    if len(t.split('.')[0]) == 1:
        t = ' ' + t
    if len(t.split('.')[1]) == 1:
        t += '0'
    return t


def float2str1p6(t):
    t = str(t)
    if len(t.split('.')[1]) == 1:
        t += '00000'
    elif len(t.split('.')[1]) == 2:
        t += '0000'
    elif len(t.split('.')[1]) == 3:
        t += '000'
    elif len(t.split('.')[1]) == 4:
        t += '00'
    elif len(t.split('.')[1]) == 5:
        t += '0'
    return t


def readEnc(trcode):
    enc = zipfile.ZipFile(f'{OPENAPI_PATH}/data/{trcode}.enc')
    lines = enc.read(trcode.upper() + '.dat').decode('cp949')
    return lines


def parseDat(trcode, lines):
    lines = lines.split('\n')
    start = [i for i, x in enumerate(lines) if x.startswith('@START')]
    end = [i for i, x in enumerate(lines) if x.startswith('@END')]
    block = zip(start, end)
    enc_data = {'trcode': trcode, 'input': [], 'output': []}
    for start, end in block:
        block_data = lines[start - 1:end + 1]
        block_info = block_data[0]
        block_type = 'input' if 'INPUT' in block_info else 'output'
        record_line = block_data[1]
        tokens = record_line.split('_')[1].strip()
        record = tokens.split('=')[0]
        fields = block_data[2:-1]
        field_name = []
        for line in fields:
            field = line.split('=')[0].strip()
            field_name.append(field)
        fields = {record: field_name}
        enc_data['input'].append(fields) if block_type == 'input' else enc_data['output'].append(fields)
    return enc_data
