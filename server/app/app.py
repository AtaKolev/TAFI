import datetime
from flask import Flask, request, render_template
import logging, traceback
from logging.handlers import RotatingFileHandler
import send_email
import download_data as dd

################################################################################################################
# APP VARIABLES
################################################################################################################
app = Flask(__name__)

app.program_last_restart = 0
app.function_password = 'imbigtrash1'
app.display_password = 'nekradikebiem2'
app.stock_watchlist = []
app.cpair_watchlist = []




################################################################################################################
# Logs:
################################################################################################################
def init_logger():
    logger = logging.getLogger('ADV')
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(level=logging.DEBUG)
    # add a log rotating handler (rotates when the file becomes 10MB, or about 100k lines):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler('logs/server.log', maxBytes=10000000, backupCount=10)
    handler.setLevel(level=logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
app.logger = init_logger()


# ERROR LOG:
def init_error_logger():
    logger = logging.getLogger('ADV ERRORS')
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(level=logging.DEBUG)
    # add a log rotating handler (rotates when the file becomes 10MB, or about 100k lines):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler('logs/server_error.log', maxBytes=10000000, backupCount=10)
    handler.setLevel(level=logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

app.error_logger = init_error_logger()

def log(func_name, message, error=False):
    if error == True:
        app.logger.error(f'{func_name}: {message}. Check server_error.log for details.')
        app.error_logger.error(f'{func_name}: {message}')
        app.error_logger.error('================')
        app.error_logger.error('ERROR TRACEBACK:')
        app.error_logger.error('================')
        app.error_logger.error(str(traceback.format_exc()))
        app.error_logger.error('================')
        subject = f"CVPN: {func_name} encountered and error"
        if app.devmode==True:
            subject += ' - DEVMODE IS ON!'
            send_email(subject, message=str(traceback.format_exc()), recipients=app.dev_emails)
        else:
            send_email(subject, message=str(traceback.format_exc()), recipients=app.dev_emails)
    else:
        app.logger.info(f'{func_name}: {message}')

def LastNlines(fname, N, phrase=None):
    text=[]
    with open(fname) as file:
        for line in (file.readlines() [-N:]):
            if phrase is not None:
                if phrase in line:
                    text.append(line)
            else:
                text.append(line)
    return text


def get_logs(length=30, search_phrase=None, logfile=None):
    if logfile is not None:
        filename = f'logs/{logfile}'
    else:
        filename='logs/server.log'
    text=''
    lines=''
    if length==0:
        lines=LastNlines(filename, 30, phrase=search_phrase)
    else:
        lines=LastNlines(filename, length, phrase=search_phrase)
    for line in lines[::-1]: #reverse to make newest on top
        text+='</br>'+line
    return text


################################################################################################################
# MANUAL FUNCTIONS
################################################################################################################


def send_test_email():
    
    message = "This is just a test"
    try:
        send_email.send_email("TAFI: Test email", message = message, recipient='atanaskolevv01@gmail.com')
        log('send_test_email', "Executed successfully!", error = False)
    except Exception as e:
        log("send_test_email", "Send test email failed!", error = True)

def add_ticker(ticker, list_to_add_to):
    list_to_add_to.append(ticker)

def print_watchlist(list_type):
    return list_type

################################################################################################################
# PAGES
################################################################################################################

@app.route('/', methods = ['GET', 'POST'])
def home():
    title = 'TAFI: Home'
    return render_template('index.html', title = title, last_restart = app.program_last_restart)

@app.route('/logs', methods = ['GET', 'POST'])
def log_visualization():
    title = 'TAFI: Logs visualization'
    if request.method == 'POST':
        boxes = request.form.getlist('mycheckbox')
        log_type = str(boxes[0])
        N_rows = int(boxes[1])
        specific_phrase = str(boxes[2])
        text = get_logs(length = N_rows, search_phrase=specific_phrase,
                        logfile=log_type)
    else:
        text = ''
    
    return render_template('logs.html', title=title, text = text)

@app.route('/function', methods = ['GET', 'POST'])
def functions():
    title = 'TAFI: Function'
    output = ''
    if request.method == 'POST':
        boxes = request.form.getlist('mycheckbox')
        function = str(boxes[0])
        password = str(boxes[1])
        if password == app.password:
            if function == 'send test email':
                send_test_email()
            elif function == 'add a stock to watchlist':
                ticker = str(boxes[2])
                add_ticker(ticker, app.stock_watchlist)
                output = f"{ticker} successfully added to Stock Watchlist!"
            elif function == 'add a currency pair to watchlist':
                ticker = str(boxes[2])
                add_ticker(ticker, app.cpair_list)
                output = f"{ticker} successfully added to CPair Watchlist!"
            elif function == 'print stock watchlist':
                output = print_watchlist(app.stock_watchlist)
            elif function == 'print cpair watchlist':
                output = print_watchlist(app.cpair_watchlist)
        else:
            output = f'<b style="color:red">REJECTED! WRONG PASSWORD!</b>'
    return render_template('function.html', title=title, output=output)



if __name__ == "__main__":
    try:
        app.program_last_restart = str(datetime.datetime.now())[:-7]
        app.run(host='0.0.0.0', port = 3000)
    except Exception as e:
        app.logger.error('Could not start TAFI!')
        app.logger.error(str(traceback.format_exc()))
    finally:
        app.logger.warning('TAFIstopped!')