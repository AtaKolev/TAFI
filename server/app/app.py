import datetime
import atexit
from flask import Flask, request, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import logging, traceback
from logging.handlers import RotatingFileHandler
import send_email
import download_data as dd
import pandas as pd
import constants as const

################################################################################################################
# APP VARIABLES
################################################################################################################
app = Flask(__name__)

app.program_last_restart = 0
app.email_recipients = ['atanaskolevv01@gmail.com']
app.function_password = 'imbigtrash1'
app.display_password = 'nekradikebiem2'
app.american_stock_watchlist = ['AAPL', 'BROS', 'PYPL', 'TSM']
app.asian_stock_watchlist = ['SE', 'SONY']
app.european_stock_watchlist = ['ABI', 'ROG', 'DSM', 'KNEBV']
app.cpair_watchlist = ['EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'USDCAD=X']
app.american_stock_open_time_hour = 16
app.american_stock_open_time_minutes = 0
app.asian_stock_open_time_hour = 3
app.asian_stock_open_time_minutes = 0
app.european_stock_open_time_hour = 10
app.european_stock_open_time_minutes = 0
app.currency_trading_hour = 0
app.currency_trading_minutes = 0





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
    except:
        log("send_test_email", "Send test email failed!", error = True)

def add_ticker(ticker, list_to_add_to):
    try:
        if ticker not in list_to_add_to:
            list_to_add_to.append(ticker)
            log('add_ticker', f"{ticker} successfuly added to {list_to_add_to}", error = False)
        else:
            log('add_ticker', f"{ticker} already in {list_to_add_to}", error = False)
    except:
        log("add_ticker", f"{ticker} was not added to {list_to_add_to}", error = True)

def print_watchlist(list_type):
    return list_type


################################################################################################################
# TIMED FUNCTIONS
################################################################################################################


def timed_stock_prediction():
    if datetime.datetime.today().weekday() not in [6,7]:
        log('timed_stock_prediction', 'Not in working days', error = False)
    else:
        hour = datetime.datetime.now().hour
        market = ''
        if hour == app.american_stock_open_time_hour:
            stocklist = app.american_stock_watchlist
            market = 'American'
        elif hour == app.asian_stock_open_time_hour:
            stocklist = app.asian_stock_watchlist
            market = 'Asian'
        elif hour == app.european_stock_open_time_hour:
            stocklist = app.european_stock_watchlist
            market = 'European'
        elif hour == app.currency_trading_hour:
            stocklist = app.cpair_watchlist
            market = 'FOREX'
        else:        
            stocklist = []
            market = ''
            log('timed_stock_prediction', 'was not in a suitable hour', error = True)
            return 0

        log('timed_stock_prediction', f"initiated for {market} market", error = False)
        message = ""
        for stock in stocklist:
            try:
                df = dd.main_pipe(ticker = stock)
                if df.loc[-1, const.predicted_change_col] == 1:
                    message += f"{market}: {stock} is probably going to go UP today by [{df.loc[-1, const.predicted_diff_col]}]!"
                    log('timed_stock_prediction', f"found a ticker that will go UP!", error = False)
                elif df.loc[-1, const.predicted_change_col] == -1:
                    message += f"{market}: {stock} is probably going to go DOWN today by [{df.loc[-1, const.predicted_diff_col]}]!"
                    log('timed_stock_prediction', f"found a ticker that will go DOWN!", error = False)
                else:
                    log('timed_stock_prediction', f"didn't find anything!", error = False)
            except:
                log('timed_stock_prediction', f"encountered an error!", error = True)
        for recipient in app.email_recipients:
            try:
                send_email.send_email(subject = f"TAFI: Daily {market} Stock Prediction",
                                      message=message,
                                      recipient = recipient)
                log('timed_stock_prediction', 'successfully sent an email', error = True)
            except:
                log('timed_stock_prediction', 'could not send an email', error = True)

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

@app.route('/display', methods = ['GET', 'POST'])
def display():
    title = 'TAFI: Display'
    output = ''
    df = pd.DataFrame()
    if request.method == 'POST':
        boxes = request.form.getlist('mycheckbox')
        ticker = str(boxes[0])
        period_back = str(boxes[1])
        interval = str(boxes[2])
        password = str(boxes[3])
        if password == app.display_password:
            try:
                df = dd.main_pipe(ticker, period_back, interval)
                output = 'Success!'
            except Exception as e:
                output = f"Failed because of\n {e}"
                log('display', f"FAILED: {e}", error = True)
        else:
            output = f'<b style="color:red">REJECTED! WRONG PASSWORD!</b>'
    
    return render_template('display.html',
                           title = title,
                           output = output,
                           table_1 = df.to_html())


@app.route('/function', methods = ['GET', 'POST'])
def functions():
    title = 'TAFI: Function'
    output = ''
    if request.method == 'POST':
        boxes = request.form.getlist('mycheckbox')
        function = str(boxes[0])
        password = str(boxes[1])
        if password == app.function_password:
            if function == 'send test email':
                send_test_email()
            elif function == 'add a stock to american watchlist':
                ticker = str(boxes[2])
                add_ticker(ticker, app.american_stock_watchlist)
                output = f"{ticker} successfully added to American Stock Watchlist!"
            elif function == 'add a stock to asian watchlist':
                ticker = str(boxes[2])
                add_ticker(ticker, app.asian_stock_watchlist)
                output = f"{ticker} successfully added to Asian Stock Watchlist!"
            elif function == 'add a stock to european watchlist':
                ticker = str(boxes[2])
                output = f"{ticker} successfully added to European Stock Watchlist!"
                add_ticker(ticker, app.european_stock_watchlist)
            elif function == 'add a currency pair to watchlist':
                ticker = str(boxes[2])
                add_ticker(ticker, app.cpair_watchlist)
                output = f"{ticker} successfully added to CPair Watchlist!"
            elif function == 'print american stock watchlist':
                output = print_watchlist(app.american_stock_watchlist)
            elif function == 'print asian stock watchlist':
                output = print_watchlist(app.asian_stock_watchlist)
            elif function == 'print european stock watchlist':
                output = print_watchlist(app.european_stock_watchlist)
            elif function == 'print cpair watchlist':
                output = print_watchlist(app.cpair_watchlist)
        else:
            output = f'<b style="color:red">REJECTED! WRONG PASSWORD!</b>'
    return render_template('function.html', title=title, output=output)



#######################################################################################
# SCHEDULED FUNCTIONS
#######################################################################################
app.scheduler = BackgroundScheduler()
app.scheduler.add_job(timed_stock_prediction, trigger = "cron", hour = app.american_stock_open_time_hour, minute = app.american_stock_open_time_minutes, end_date = '2200-01-01')
app.scheduler.add_job(timed_stock_prediction, trigger = "cron", hour = app.asian_stock_open_time_hour, minute = app.asian_stock_open_time_minutes, end_date = '2200-01-01')
app.scheduler.add_job(timed_stock_prediction, trigger = "cron", hour = app.european_stock_open_time_hour, minute = app.european_stock_open_time_minutes, end_date = '2200-01-01')
app.scheduler.add_job(timed_stock_prediction, trigger = "cron", hour = app.european_stock_open_time_hour, minute = app.currency_trading_hour, end_date = '2200-01-01')
app.scheduler.start()
atexit.register(lambda: app.scheduler.shutdown())




if __name__ == "__main__":
    try:
        app.program_last_restart = str(datetime.datetime.now())[:-7]
        app.run(host='0.0.0.0', port = 3000)
    except Exception as e:
        app.logger.error('Could not start TAFI!')
        app.logger.error(str(traceback.format_exc()))
    finally:
        app.logger.warning('TAFIstopped!')