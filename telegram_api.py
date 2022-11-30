TOKEN = ''

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from session import Session
from models import *
from datetime import datetime
from os.path import exists, isdir
from os import mkdir, getcwd

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

(LOGIN, ENTERING_LOGIN, ENTERING_PASSWORD, IN_SYSTEM,
CUST_INFO, CUSTOMER_NOT_FOUND, CUSTOMER_FOUND, CONTACT_SEARCHED,
ADD_TASK_WRITE, ADD_TASK_TYPE, ADD_TASK_PRIORITY, ADD_TASK_FINAL,
CHANGE_TASK_NAME, ADD_TASK_VALIDATE, CHANGE_TASK_CLOSING_DATE, CHANGE_EXEC_PERIOD,
CHANGE_EXECUTOR, CHANGE_CUSTOMER, CHANGE_TYPE, CHANGE_PRIORITY,
NEW_USER_LOGIN, NEW_USER_PASSWORD, NEW_USER_NAME, NEW_USER_POSITION,
CHANGE_USER_NAME, NEW_USER_CHECK, CHANGE_USER_LOGIN, CHANGE_USER_PASSWORD,
CHANGE_USER_POSITION, MAKE_REPORT_CHECK, MAKE_REPORT_S_DATE, MAKE_REPORT_F_DATE,
MAKE_REPORT) = range(33)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.user_data
    if 'login' in data:
        if 'password' in data:
            return await main_menu(update, context)
    keyboard = [['Login']]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("You are logged out.", reply_markup=reply_markup)
    return LOGIN


async def start_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Enter login:')
    return ENTERING_LOGIN


async def restart_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Incorrect login of password!\nPlease retry.')
    context.user_data.clear()
    return await start_login(update, context)

async def recieve_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['login'] = update.message.text.strip()
    await update.message.reply_text('Enter password:')
    return ENTERING_PASSWORD


async def recieve_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    context.user_data['password'] = password
    try:
        sess = Session(context.user_data['login'], password)
        context.user_data['sess'] = sess
        
        await update.message.reply_markdown_v2(f'You logged in as _{sess.employee.emp_name}_ *\({sess.position_name}\)*')
        await main_menu(update, context)
        return IN_SYSTEM
    except Exception as e:
        print(e.with_traceback())
        return await restart_login(update, context)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    
    keyboard = [[]]
    if sess.employee.emp_position == 2:
        keyboard = [['All tasks', 'All customers'], 
                    ['All contracts', 'All equipment'],
                    ['Add employee', 'Add task'], 
                    ['Customer info', 'Make employee report'],
                    ['Done']]
    elif sess.employee.emp_position == 1:
        keyboard = [['Tasks', 'Customer info'],
                    ['Change task executor', 'Make employee report'],
                    ['Done']]
    else:
        keyboard = [['Tasks', 'Customer info'], 
                    ['Done']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_markdown_v2("Available functions", reply_markup=reply_markup)
    return IN_SYSTEM


async def print_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    tasks = sess.get_all_tasks()
    for task in tasks:
        await update.message.reply_markdown_v2(task)
    return IN_SYSTEM


async def customer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = ReplyKeyboardRemove()
    await update.message.reply_text('Type customer name:', reply_markup=markup)
    return CUST_INFO


async def get_customer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    customer_name = update.message.text
    customer = sess.get_customer_info(customer_name)
    if customer is None:
        keyboard = [['Retry', 'Back to main menu']]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_markdown_v2('*Customer not found*', reply_markup=markup)
        return CUSTOMER_NOT_FOUND

    keyboard = [['Print contacts', 'Main menu'],['Done']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_markdown_v2(str(customer), reply_markup=markup)
    context.user_data['customer'] = customer
    return CUSTOMER_FOUND


async def print_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    customer = context.user_data['sustomer']

    contacts = sess.get_contacts_info(customer.customer_id)
    keyboard = [['Search another customer', 'Main menu'], ['Done']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    if contacts is None:
        await update.message.reply_markdown_v2('*No contacts found*', reply_markup=markup)
        return CONTACT_SEARCHED
    
    for contact in contacts:
        await update.message.reply_markdown_v2(str(contact))

    await update.message.reply_markdown_v2("What's next?", reply_markup=markup)
    return CONTACT_SEARCHED


async def print_all_customers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    customers = sess.get_all_customers()
    if customers is None:
        await update.message.reply_markdown_v2('*No customers found*')
        return main_menu(update, context)
    
    for customer in customers:
        await update.message.reply_markdown_v2(str(customer))
    return await main_menu(update, context)


async def print_all_contracts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    contracts = sess.get_all_contracts()
    if contracts is None:
        await update.message.reply_markdown_v2('*No contracts found*')
        return main_menu(update, context)

    for contract in contracts:
        await update.message.reply_markdown_v2(contract)
    return await main_menu(update, context)


async def print_all_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    equipment = sess.get_all_equipment()
    if equipment is None:
        await update.message.reply_markdown_v2('*No equipment is found*')
        return main_menu(update, context)

    for eq in equipment:
        await update.message.reply_markdown_v2(str(eq))
    return await main_menu(update, context)


async def add_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    context.user_data['new_task_dict'] = {}

    new_task_dict = context.user_data['new_task_dict']
    markup = ReplyKeyboardRemove()
    creating_date = str(datetime.now().date())
    task = Task(creating_date=creating_date, author_id=sess.employee.employee_id)
    context.user_data['task'] = task

    await update.message.reply_markdown_v2(prepare_to_markdown(
        """Type task parameters in folowing format:\n
_Task name_
_Closing date (YYYY-MM-DD format)_
_Execution period in weeks_
_Executor login_
_Customer name_\n
*All undefined parameters replace with -*"""
    ), reply_markup=markup)

    new_task_dict['creating_date'] = creating_date
    new_task_dict['author'] = sess.employee.emp_name
    return ADD_TASK_WRITE


async def add_task_write(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    params = update.message.text.split('\n')
    
    if len(params) != 5:
        await update.message.reply_text('Incorrect input')
        return await add_task_start(update, context)

    (name,
    closing_date,
    exec_period,
    executor,
    customer) = params

    if not is_closing_date(closing_date):
        await update.message.reply_text('Incorrect closing date')
        return await add_task_start(update, context)

    task.task_name = name
    task.closing_date = closing_date
    task.exec_period = exec_period

    executor = sess.get_employee_info(executor)
    if executor is None:
        await update.message.reply_text('Employee not found. Try again')
        return await add_task_start(update, context)
    task.executor_id = executor.employee_id

    customer = sess.get_customer_info(customer)
    if customer is None:
        await update.message.reply_text('Customer not found. Try again')
        return await add_task_start(update, context)
    task.customer_id = customer.customer_id

    task_types = sess.get_all_task_types()
    if task_types is None:
        await update.message.reply_text('Something went wrong...')
        return IN_SYSTEM
    keyboard = [[]]
    for type in task_types:
        keyboard.append([InlineKeyboardButton(str(type), callback_data=str(type.task_type_id))])
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose task type', reply_markup=markup)
    
    new_task_dict['name'] = name
    new_task_dict['closing_date'] = str(closing_date)
    new_task_dict['exec_period'] = exec_period
    new_task_dict['executor'] = executor.emp_name
    new_task_dict['customer'] = customer.customer_name

    return ADD_TASK_TYPE


async def add_task_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(None)
    task.task_type_id = int(query.data)
    new_task_dict['task_type'] = sess.get_task_type_name(int(query.data)).task_type_name
    keyboard = [
        [InlineKeyboardButton('High', callback_data='1')],
        [InlineKeyboardButton('Medium', callback_data='2')],
        [InlineKeyboardButton('Low', callback_data='3')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('Choose task priority', reply_markup=markup)

    return ADD_TASK_PRIORITY


async def add_task_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(None)
    task.priority_code = int(query.data)
    new_task_dict['priority'] = sess.get_task_priority_info(int(query.data)).priority_name

    keyboard = [
        [InlineKeyboardButton('Change name', callback_data='name')],
        [InlineKeyboardButton('Change closing date', callback_data='clos_date')],
        [InlineKeyboardButton('Change execution period', callback_data='exec_per')],
        [InlineKeyboardButton('Change executor', callback_data='executor')],
        [InlineKeyboardButton('Change customer', callback_data='customer')],
        [InlineKeyboardButton('Change task type', callback_data='type')],
        [InlineKeyboardButton('Change priority', callback_data='priority')],
        [InlineKeyboardButton('Correct', callback_data='correct')]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text('Check all task fields')
    await query.message.reply_markdown_v2(convert_dict_to_task(new_task_dict), reply_markup=markup)
    return ADD_TASK_FINAL


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_task_dict = context.user_data['new_task_dict']

    keyboard = [
        [InlineKeyboardButton('Change name', callback_data='name')],
        [InlineKeyboardButton('Change closing date', callback_data='clos_date')],
        [InlineKeyboardButton('Change execution period', callback_data='exec_per')],
        [InlineKeyboardButton('Change executor', callback_data='executor')],
        [InlineKeyboardButton('Change customer', callback_data='customer')],
        [InlineKeyboardButton('Change task type', callback_data='type')],
        [InlineKeyboardButton('Change priority', callback_data='priority')],
        [InlineKeyboardButton('Correct', callback_data='correct')]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Check all task fields')
    await update.message.reply_markdown_v2(convert_dict_to_task(new_task_dict), reply_markup=markup)
    return ADD_TASK_FINAL


async def change_task_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text('Enter new name:')
    return CHANGE_TASK_NAME


async def change_task_name_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    task.task_name = update.message.text.strip()
    new_task_dict['name'] = task.task_name
    return await validate(update, context)


async def change_closing_date_start(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    if first:
        query = update.callback_query
        await query.answer()
    else: query = update
    await query.message.reply_text('Enter new date(YYYY-MM-DD):')
    return CHANGE_TASK_CLOSING_DATE


async def change_closing_date_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    date = update.message.text
    if is_closing_date(date):
        task.closing_date = date
        new_task_dict['closing_date'] = date
        return await validate(update, context)

    await update.message.reply_text('Incorrect closing date')
    return change_closing_date_start(update, context, False)


async def change_exec_per_start(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    if first:
        query = update.callback_query
        await query.answer()
    else: query = update
    await query.message.reply_text('Enter new execution period:')
    return CHANGE_EXEC_PERIOD

async def change_exec_per_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    weeks = update.message.text.strip()
    if weeks.isnumeric():
        task.exec_period = weeks
        new_task_dict['exec_period'] = weeks
        return await validate(update, context)
    
    await update.message.reply_text('Incorrect input')
    return change_exec_per_start(update, context, False)


async def change_executor_start(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    if first:
        query = update.callback_query
        await query.answer()
    else: query = update
    await query.message.reply_text('Enter new employee\'s login:')
    return CHANGE_EXECUTOR

async def change_executor_end(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    executor = update.message.text.strip()
    executor = sess.get_employee_info(executor)
    if executor is not None:
        task.executor_id = executor.employee_id
        new_task_dict['executor'] = executor.emp_name
        return await validate(update, context)
    
    await update.message.reply_text('Employee not found')
    return change_exec_per_start(update, context, False)


async def change_customer_start(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    if first:
        query = update.callback_query
        await query.answer()
    else: query = update
    await query.message.reply_text('Enter new customer\'s name:')
    return CHANGE_CUSTOMER

async def change_customer_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    customer = update.message.text.strip()
    customer = sess.get_customer_info(customer)
    if customer is not None:
        task.customer_id = customer.customer_id
        new_task_dict['customer'] = customer.customer_name
        return await validate(update, context)
    
    await update.message.reply_text('customer not found')
    return change_exec_per_start(update, context, False)


async def change_type_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']

    query = update.callback_query
    await query.answer()
    task_types = sess.get_all_task_types()
    if task_types is None:
        await query.message.reply_text('Something went wrong...')
        return IN_SYSTEM
    keyboard = [[]]
    for type in task_types:
        keyboard.append([InlineKeyboardButton(str(type), callback_data=str(type.task_type_id))])
    markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('Choose task type', reply_markup=markup)

    return CHANGE_TYPE

async def change_type_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    query = update.callback_query
    await query.answer()
    task.task_type_id = int(query.data)
    type = sess.get_task_type_name(int(query.data))
    new_task_dict['task_type'] = type.task_type_name

    return await validate(query, context)


async def change_priority_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton('High', callback_data='1')],
        [InlineKeyboardButton('Medium', callback_data='2')],
        [InlineKeyboardButton('Low', callback_data='3')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('Choose task priority', reply_markup=markup)
    
    return CHANGE_PRIORITY

async def change_priority_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    query = update.callback_query
    await query.answer()
    task.priority_code = int(query.data)
    priority = sess.get_task_priority_info(int(query.data))
    new_task_dict['priority'] = priority.priority_name

    return await validate(query, context)

async def add_task_end(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    sess: Session = context.user_data['sess']
    new_task_dict = context.user_data['new_task_dict']
    task: Task = context.user_data['task']

    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(None)

    try:
        sess.add_new_task(task)
        await query.edit_message_text('Task added')
        await query.message.reply_markdown_v2(convert_dict_to_task(new_task_dict))

    except Exception as e:
        e.with_traceback()
        await query.edit_message_text('Something went wrong...')

    finally:
        del context.user_data['new_task_dict']
        del context.user_data['task']
        await main_menu(query, context)
        return IN_SYSTEM


async def add_employee_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['employee'] = Employee()
    markup = ReplyKeyboardRemove()
    await update.message.reply_markdown_v2('Enter login:', reply_markup=markup)
    return NEW_USER_LOGIN


async def add_employee_login(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    sess: Session = context.user_data['sess']
    employee: Employee = context.user_data['employee']
    
    if first:
        login = update.message.text
        if sess.employee_exists(login):
            await update.message.reply_markdown_v2('*User already exists*')
            return  await add_employee_start(update, context)
        elif len(login) > 20:
            await update.message.reply_markdown_v2('*Login is too long*')
            return await add_employee_start(update, context)

        employee.emp_login = login
    await update.message.reply_text('Enter password:')
    return NEW_USER_PASSWORD


async def add_employee_password(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    employee: Employee = context.user_data['employee']

    if first:
        password = update.message.text
        if len(password) > 50:
            await update.message.reply_markdown_v2('*Password is too long*')
            return await add_employee_login(update, context, False)
        
        employee.emp_password = password

    await update.message.reply_text('Enter full name of employee:')
    return NEW_USER_NAME


async def add_employee_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    employee: Employee = context.user_data['employee']

    name = update.message.text
    if len(name) > 100:
        await update.message.reply_markdown_v2('*Too much characters*')
        return await add_employee_password(update, context, False)

    employee.emp_name = name

    keyboard = [
        [InlineKeyboardButton('Manager', callback_data='1'),
        InlineKeyboardButton('Worker', callback_data='0')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose position:', reply_markup=markup)
    return NEW_USER_POSITION


async def add_employee_position(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    employee: Employee = context.user_data['employee']

    query = update
    if first:
        query = update.callback_query
        await query.answer()
        await query.edit_message_reply_markup(None)
        position = query.data

        if position == '1':
            employee.emp_position = 1
        else:
            employee.emp_position = 0

    keyboard = [
        [InlineKeyboardButton('Change login', callback_data='login')],
        [InlineKeyboardButton('Change password', callback_data='password')],
        [InlineKeyboardButton('Change name', callback_data='name')],
        [InlineKeyboardButton('Change position', callback_data='position')],
        [InlineKeyboardButton('Correct', callback_data='correct')]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    hidden_password = '\*' * (len(employee.emp_password) - 3) + employee.emp_password[-3:]
    position_name = 'manager' if employee.emp_position == 1 else 'worker'

    await query.message.reply_text('Check all fields:')
    await query.message.reply_markdown_v2(prepare_to_markdown(
        f'*Login:* {employee.emp_login}\n'+
        f'*Password:* {hidden_password}\n'+
        f'*Name*: {employee.emp_name}\n'
        f'*Position:* {position_name}'),
        reply_markup=markup)

    return NEW_USER_CHECK

    
async def change_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    query = update
    if first:
        query = update.callback_query
        await query.answer()
        await query.edit_message_reply_markup(None)

    await query.message.reply_text('Enter new name:', reply_markup=ReplyKeyboardRemove())
    return CHANGE_USER_NAME

async def change_user_name_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    employee: Employee = context.user_data['employee']

    name = update.message.text
    if len(name) > 100:
        await update.message.reply_markdown_v2('*Too much characters*')
        return await change_user_name(update, context, False)
    employee.emp_name = name
    
    return await add_employee_position(update, context, False)


async def change_user_login(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    query = update
    if first:
        query = update.callback_query
        await query.answer()
        await query.edit_message_reply_markup(None)

    await query.message.reply_text('Enter new login:')
    return CHANGE_USER_LOGIN

async def change_user_login_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    employee: Employee = context.user_data['employee']

    login = update.message.text
    if sess.employee_exists(login):
        await update.message.reply_markdown_v2('*User already exists*')
        return await change_user_login(update, context, False)
    elif len(login) > 20:
        await update.message.reply_markdown_v2('*Login is too long*')
        return await change_user_login(update, context, False)

    employee.emp_login = login

    return await add_employee_position(update, context, False)


async def change_user_password(update: Update, context: ContextTypes.DEFAULT_TYPE, first=True):
    query = update
    if first:
        query = update.callback_query
        await query.answer()
        await query.edit_message_reply_markup(None)

    await query.message.reply_text('Enter new password:', reply_markup=ReplyKeyboardRemove())
    return CHANGE_USER_PASSWORD

async def change_user_password_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    employee: Employee = context.user_data['employee']

    password = update.message.text
    if len(password) > 50:
        await update.message.reply_markdown_v2('*Password is too long*')
        return await change_user_password(update, context, False)
    
    employee.emp_password = password
    return await add_employee_position(update, context, False)


async def change_user_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()
    await query.edit_message_reply_markup(None)

    keyboard = [
        [InlineKeyboardButton('Manager', callback_data='1'),
        InlineKeyboardButton('Worker', callback_data='0')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose position:', reply_markup=markup)
    return CHANGE_USER_POSITION

async def change_user_position_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    employee: Employee = context.user_data['employee']
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(None)
    position = query.data

    if position == '1':
        employee.emp_position = 1
    else:
        employee.emp_position = 0

    return await add_employee_position(update, context, False)


async def add_employee_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(None)

    try:
        sess.add_new_employee(employee)
        await query.message.reply_text('Employee added')
    except Exception as e:
        e.with_traceback()
        await query.message.reply_text('Something went wrong...')
    
    employee = None
    return await main_menu(query, context)

async def make_report_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = ReplyKeyboardRemove()
    await update.message.reply_text('Enter employee login/name:', reply_markup=markup)
    context.user_data['new_emp_report'] = {}
    return MAKE_REPORT_CHECK

async def make_report_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_emp_report = context.user_data['new_emp_report']

    employee = update.message.text
    employee = sess.get_employee_info(employee)

    if employee is None:
        await update.message.reply_markdown_v2('*Employee not found*')
        return await make_report_start(update, context)
    
    new_emp_report['employee_id'] = employee.employee_id
    new_emp_report['emp_login'] = employee.emp_login
    await update.message.reply_markdown_v2(str(employee))
    keyboard = [
        [InlineKeyboardButton('Yes', callback_data='yes'),
        InlineKeyboardButton('No', callback_data='no')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Is that correct employee?', reply_markup=markup)
    return MAKE_REPORT_F_DATE


async def make_report_incorr_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    query.edit_message_reply_markup(None)
    query.message.reply_text('Try to type more of employee name/login')
    query.delete_message()
    return make_report_start(update, context)


async def make_report_first_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(None)
    await query.message.reply_text('Enter starting date of report (YYYY-MM-DD)')
    await query.delete_message()
    return MAKE_REPORT_S_DATE


async def make_report_closing_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_emp_report = context.user_data['new_emp_report']

    date = update.message.text
    if is_date(date):
        new_emp_report['starting_date'] = date
        await update.message.reply_text('Enter closing date (YYYY-MM-DD)')
        return MAKE_REPORT

    await update.message.reply_markdown_v2('*Incorrect input*')
    await update.message.reply_text('Enter starting date of report (YYYY-MM-DD)')
    return MAKE_REPORT_S_DATE


async def make_report_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sess: Session = context.user_data['sess']
    new_emp_report = context.user_data['new_emp_report']

    date = update.message.text
    if not is_date(date):
        await update.message.reply_markdown_v2('*Incorrect input*')
        await update.message.reply_text('Enter closing date (YYYY-MM-DD)')
        return MAKE_REPORT_S_DATE
    
    new_emp_report['closing date'] = date        

    if not isdir('reports'):
        mkdir('reports')

    i = 1
    filepath = ''
    while True:
        filepath = getcwd() + (f'\\reports\\{new_emp_report["emp_login"]}_'+
            f'{new_emp_report["starting_date"]}-{new_emp_report["closing date"]}_{i}.csv')
        if exists(filepath):
            continue
        break

    try:
        sess.make_emp_report(
            new_emp_report['employee_id'],
            new_emp_report['starting_date'],
            new_emp_report['closing date'],
            filepath
        )
        with open(filepath, 'rb') as file:
            await update.message.reply_document(file)
        new_emp_report.clear()
        
    except Exception as e:
        e.with_traceback()
        await update.message.reply_text('Something went wrong...')

    finally:
        return await main_menu(update, context)


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Ok. To start again, enter "/start"')
    return ConversationHandler.END


def is_date(text: str) -> bool:
    y, m, d = text.split('-')
    try:
        date = datetime(int(y), int(m), int(d))
        return True
    except:
        return False

def is_closing_date(text: str) -> bool:
    y, m, d = text.split('-')
    try:
        date = datetime(int(y), int(m), int(d))
        now = datetime.now()
        if date < now:
            return False
        return True
    except:
        return False

def convert_dict_to_task(task: dict):
    result = (f"""{task['name']}\n"""+
            f"""   *Creating date:* {str(task['creating_date'])}\n"""+
            f"""   *Closing date:* {str(task['closing_date'])}\n"""+
            f"""   *Weeks to compleate:* {task['exec_period']}\n"""+
            f"""   *Author:* {task['author']}\n"""+
            f"""   *Executor:* {task['executor']}\n"""+
            f"""   *Customer:* {task['customer']}\n"""+
            f"""   *Task type:* {task['task_type']}\n"""+
            f"""   *Priority:* {task['priority']}\n""")

    return prepare_to_markdown(result)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    starting_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOGIN:[
                MessageHandler(filters.Regex('^Login$'), start_login),
                CommandHandler("start", start)
                ],
            ENTERING_LOGIN:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, recieve_login),
                CommandHandler("start", start)
                ],
            ENTERING_PASSWORD:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, recieve_password),
                CommandHandler("start", start)
                ],
            IN_SYSTEM:[
                MessageHandler(filters.Regex('^Tasks|All tasks$'), print_tasks),
                MessageHandler(filters.Regex('^Customer info$'), customer_info),
                MessageHandler(filters.Regex('^All customers$'), print_all_customers),
                MessageHandler(filters.Regex('^All contracts$'), print_all_contracts),
                MessageHandler(filters.Regex('^All equipment$'), print_all_equipment),
                MessageHandler(filters.Regex('^Add task$'), add_task_start),
                MessageHandler(filters.Regex('^Add employee$'), add_employee_start),
                MessageHandler(filters.Regex('^Make employee report$'), make_report_start),
                CommandHandler("start", start)
                ],
            CUST_INFO:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_customer_info),
                CommandHandler("start", start)
            ],
            CUSTOMER_NOT_FOUND:[
                MessageHandler(filters.Regex('^Retry$'), customer_info),
                MessageHandler(filters.Regex('^Main menu$'), main_menu),
                CommandHandler("start", start)
            ],
            CUSTOMER_FOUND:[
                MessageHandler(filters.Regex('^Print contacts$'), print_contacts),
                MessageHandler(filters.Regex('^Main menu$'), main_menu),
                CommandHandler("start", start)
            ],
            CONTACT_SEARCHED:[
                MessageHandler(filters.Regex('^Search another customer$'), customer_info),
                MessageHandler(filters.Regex('^Main menu$'), main_menu),
                CommandHandler("start", start)
            ],
            ADD_TASK_WRITE:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_write)
            ],
            ADD_TASK_TYPE:[
                CallbackQueryHandler(add_task_type)
            ],
            ADD_TASK_PRIORITY:[
                CallbackQueryHandler(add_task_priority)
            ],
            ADD_TASK_FINAL:[
                CallbackQueryHandler(change_task_name_start, pattern='^name$'),
                CallbackQueryHandler(change_closing_date_start, pattern='^clos_date$'),
                CallbackQueryHandler(change_exec_per_start, pattern='^exec_per$'),
                CallbackQueryHandler(change_executor_start, pattern='^executor$'),
                CallbackQueryHandler(change_customer_start, pattern='^customer$'),
                CallbackQueryHandler(change_type_start, pattern='^type$'),
                CallbackQueryHandler(change_priority_start, pattern='^priority$'),
                CallbackQueryHandler(add_task_end, pattern='^correct$')
            ],
            CHANGE_TASK_NAME:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_task_name_end)
            ],
            CHANGE_TASK_CLOSING_DATE:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_closing_date_end)
            ],
            CHANGE_EXEC_PERIOD:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_exec_per_end)
            ],
            CHANGE_EXECUTOR:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_executor_end)
            ],
            CHANGE_CUSTOMER:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_customer_end)
            ],
            CHANGE_TYPE:[
                CallbackQueryHandler(change_type_end)
            ],
            CHANGE_PRIORITY:[
                CallbackQueryHandler(change_priority_end)
            ],
            NEW_USER_LOGIN:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_employee_login)
            ],
            NEW_USER_PASSWORD:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_employee_password)
            ],
            NEW_USER_NAME:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_employee_name)
            ],
            NEW_USER_POSITION:[
                CallbackQueryHandler(add_employee_position)
            ],
            NEW_USER_CHECK:[
                CallbackQueryHandler(change_user_login, pattern='^login$'),
                CallbackQueryHandler(change_user_password, pattern='^password$'),
                CallbackQueryHandler(change_user_name, pattern='^name$'),
                CallbackQueryHandler(change_user_position, pattern='^position$'),
                CallbackQueryHandler(add_employee_end, pattern='^correct$'),
            ],
            CHANGE_USER_LOGIN:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_user_login_end)
            ],
            CHANGE_USER_PASSWORD:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_user_password_end)
            ],
            CHANGE_USER_NAME:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_user_name_end)
            ],
            CHANGE_USER_POSITION:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_user_position_end)
            ],
            MAKE_REPORT_CHECK:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, make_report_check)
            ],
            MAKE_REPORT_F_DATE:[
                CallbackQueryHandler(make_report_first_date, pattern='^yes$'),
                CallbackQueryHandler(make_report_incorr_employee, pattern='^no$')
            ],
            MAKE_REPORT_S_DATE:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, make_report_closing_date)
            ],
            MAKE_REPORT:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, make_report_end)
            ]
        },
        fallbacks=[MessageHandler(filters.Regex('^Done$'), done)]
    )


    application.add_handler(starting_conv)
    application.run_polling()



if __name__ == "__main__":
    main()
