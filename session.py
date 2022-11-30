import psycopg2 as pg
from models import *
import datetime

HOST = 'localhost'
PORT = 5432
DATABASE = 'contacts'

class Session:
    def __init__(self, login, password):
        self.connection = pg.connect(
                host=HOST,
                port=PORT,
                dbname=DATABASE,
                user=login,
                password=password
            )

        self.cursor = self.connection.cursor()
        query = f"""SELECT (employee_id, emp_position, emp_name, emp_login)
                FROM employee
                WHERE emp_login = '{login}'"""
        self.cursor.execute(query)

        params = self.cursor.fetchall()[0][0][1:-1].split(',')
        self.employee = Employee(
            int(params[0]),
            int(params[1]),
            params[2][1:-1],
            params[3]
        )
        self.position_name = ''
        if self.employee.emp_position == 2:
            self.position_name = 'administrator'
        elif self.employee.emp_position == 1:
            self.position_name = 'manager'
        else:
            self.position_name = 'worker'


    def get_all_tasks(self):
        self.cursor.execute(
            """SELECT
                    task_id,
                    task_name,
                    creating_date,
                    closing_date,
                    exec_period,
                    ea.emp_name AS author,
                    ee.emp_name AS executor,
                    customer_name AS customer,
                    task_type_name AS task_type,
                    priority_type as priority,
                    task_completed
                FROM task t
                JOIN employee ea ON t.author_id = ea.employee_id
                JOIN employee ee ON t.executor_id = ee.employee_id
                JOIN customer c ON t.customer_id = c.customer_id
                JOIN task_type_classifier ts ON t.task_type_id = ts.task_type_id
                JOIN prior_classifier p ON t.priority_code = p.priority_code"""
        )

        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return ["Looks like you don't have tasks yet."]
        result = []
        for i,row in enumerate(answer):
            row = ['~Undefined~' if x == None else x for x in row]
            result.append((f"""{i+1}\. {row[1]}\n"""+
             f"""   *Creating date:* {str(row[2])}\n"""+
             f"""   *Closing date:* {str(row[3])}\n"""+
             f"""   *Weeks to compleate:* {row[4]}\n"""+
             f"""   *Author:* {row[5]}\n"""+
             f"""   *Executor:* {row[6]}\n"""+
             f"""   *Customer:* {row[7]}\n"""+
             f"""   *Task type:* {row[8]}\n"""+
             f"""   *Priority:* {row[9]}\n"""+
             f"""   *{'Completed' if row[10] else 'Not completed'}*""").replace('-', '\-'))

        return result


    def get_all_customers(self):
        self.cursor.execute(
            """SELECT * FROM customer"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None
        
        customers = []
        for row in answer:
            customers.append(Customer(
                row[0], row[1], row[2], row[3], row[4]
            ))
        
        return customers


    def get_all_contracts(self):
        self.cursor.execute(
            """SELECT
                contract_number,
                contract_name,
                customer_name,
                contract_price 
            FROM contract ctr
            JOIN customer cst ON ctr.customer_id = cst.customer_id"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None
        
        contracts = []
        for i,row in enumerate(answer):
            contract = (
                f"""{i+1}.*Contract number:* {row[0]}\n"""+
                f"""   *Contract name:* {row[1]}\n"""+
                f"""   *Customer:* {row[2]}\n"""+
                f"""   *Total price:* {float(row[3])}""")
            contract = contract.replace('-', '\-').replace('.', '\.')
            contract = contract.replace('+', '\+').replace('_', '\_')
            contracts.append(contract)

        return contracts

    def get_all_equipment(self):
        self.cursor.execute(
            """SELECT * FROM equipment"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None

        equipment = []
        for eq in answer:
            equipment.append(Equipment(
                eq[0], eq[1]
            ))
        return equipment

    
    def get_all_task_types(self):
        self.cursor.execute(
            """SELECT * FROM task_type_classifier"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None

        types = []
        for type in answer:
            types.append(TaskTypeClassifier(
                type[0], type[1]
            ))
        return types


    def add_new_task(self, task: Task):
        self.cursor.execute(
            f"""INSERT INTO task(
                task_name,
                creating_date,
                closing_date,
                exec_period,
                author_id,
                executor_id,
                customer_id,
                task_type_id,
                priority_code,
                task_completed
            ) VALUES
            (
                '{task.task_name}',
                '{task.creating_date}',
                '{task.closing_date}',
                {task.exec_period},
                {task.author_id},
                {task.executor_id},
                {task.customer_id},
                {task.task_type_id},
                {task.priority_code},
                {task.task_completed}
            )"""
        )
        self.connection.commit()


    def add_new_employee(self, employee: Employee):
        self.cursor.execute(
            f"""CALL add_employee(
                '{employee.emp_login}',
                '{employee.emp_password}',
                {employee.emp_position},
                '{employee.emp_name}')"""
        )
        self.connection.commit()


    def make_emp_report(self, employee_id, starting_date, ending_date, filepath):
        self.cursor.execute(
            f"""CALL export_to_csv(
                {employee_id},
                '{str(starting_date)}',
                '{ending_date}',
                '{filepath}'
            )"""
        )

    def mark_task_compleated(self, task_id):
        self.cursor.execute(
            f"""UPDATE task SET task_completed = true
            WHERE task_id = {task_id}"""
        )


    def change_executor(self, task_id, executor_id):
        self.cursor.execute(
            f"""UPDATE task SET executor_id = {executor_id} WHERE task_id = {task_id}"""
        )


    def change_exec_period(self, task_id, new_period):
        self.cursor.execute(
            f"""UPDATE task SET exec_period = {new_period} WHERE task_id = {task_id}"""
        )

    
    def get_task_type_name(self, type_id: int) -> TaskTypeClassifier:
        self.cursor.execute(
            f"""SELECT * FROM task_type_classifier WHERE task_type_id = {type_id}"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None

        answer = answer[0]
        type = TaskTypeClassifier(answer[0], answer[1])
        
        return type

    def get_task_priority_info(self, priority_code: int) -> PriorClassifier:
        self.cursor.execute(
            f"""SELECT * FROM prior_classifier WHERE priority_code = {priority_code}"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None

        answer = answer[0]
        priority = PriorClassifier(answer[0], answer[1])

        return priority


    def get_contacts_info(self, customer_id) -> list:
        self.cursor.execute(
            f"""SELECT * FROM contact_person WHERE customer_id = {customer_id}"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None
        
        contact_persons = []
        for person in answer:
            contact_persons.append(ContactPerson(customer_id, person[1], person[2], person[3], person[4]))

        return contact_persons
    
    def get_employee_info(self, employee: str) -> Employee:
        employee = employee.lower()
        self.cursor.execute(
            f"""SELECT
                employee_id,
                emp_position,
                emp_name,
                emp_login
             FROM employee
             WHERE LOWER(emp_name) LIKE '%%{employee}%%' OR
             LOWER(emp_login) LIKE '%%{employee}%%'"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None

        answer = answer[0]

        employee = Employee(answer[0], answer[1], answer[2], answer[3])
        return employee


    def get_customer_info(self, customer_name: str):
        customer_name = customer_name.lower()
        self.cursor.execute(
            f"""SELECT * FROM customer WHERE LOWER(customer_name) LIKE '%%{customer_name}%%'"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0:
            return None

        answer = answer[0]

        customer = Customer(answer[0], answer[1], answer[2], answer[3], answer[4])
        
        return customer


    def employee_exists(self, login: str) -> bool:
        self.cursor.execute(
            f"""SELECT emp_login FROM employee WHERE emp_login = '{login}'"""
        )
        answer = self.cursor.fetchall()
        if len(answer) == 0: return False
        return True


    def convert_task_to_str(self, task: Task) -> str:
        self.cursor.execute(
            f"""SELECT
                    task_id,
                    task_name,
                    creating_date,
                    closing_date,
                    exec_period,
                    ea.emp_name AS author,
                    ee.emp_name AS executor,
                    customer_name AS customer,
                    task_type_name AS task_type,
                    priority_type as priority,
                    task_completed
                FROM task t
                JOIN employee ea ON t.author_id = ea.employee_id
                JOIN employee ee ON t.executor_id = ee.employee_id
                JOIN customer c ON t.customer_id = c.customer_id
                JOIN task_type_classifier ts ON t.task_type_id = ts.task_type_id
                JOIN prior_classifier p ON t.priority_code = p.priority_code
                WHERE task_id = {task.task_id}"""
        )
        answer = self.cursor.fetchall()

        answer = ['~Undefined~' if x == None else x for x in answer]
        result = (f"""{answer[1]}\n"""+
            f"""   *Creating date:* {str(answer[2])}\n"""+
            f"""   *Closing date:* {str(answer[3])}\n"""+
            f"""   *Weeks to compleate:* {answer[4]}\n"""+
            f"""   *Author:* {answer[5]}\n"""+
            f"""   *Executor:* {answer[6]}\n"""+
            f"""   *Customer:* {answer[7]}\n"""+
            f"""   *Task type:* {answer[8]}\n"""+
            f"""   *Priority:* {answer[9]}\n"""+
            f"""   *{'Completed' if answer[10] else 'Not completed'}*""")
        
        result = prepare_to_markdown(result)


