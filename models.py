class ContactPerson:
    def __init__(
        self,
        customer_id: int,
        contact_serial: int,
        full_name: str,
        contact_ph_number: str,
        contact_email: str
    ):
        self.customer_id = customer_id
        self.contact_serial = contact_serial
        self.full_name = full_name
        self.contact_ph_number = contact_ph_number
        self.contact_email = contact_email

    def __str__(self) -> str:
        phone_number = self.contact_ph_number if self.contact_ph_number != None else '~Undefined~'
        email = self.contact_email if self.contact_email != None else '~Undefined~'
        result = (f"""{self.contact_serial}. *{self.full_name}*\n"""+
                f"""*Phone number:* {self.contact_ph_number}\n"""+
                f"""*Email:* {self.contact_email}""")
        return prepare_to_markdown(result)



class Contract:
    def __init__(
        self,
        contract_number: int,
        contract_name: str,
        customer_id: int,
        contract_price: float
    ):
        self.contract_number = contract_number
        self.contract_name = contract_name
        self.customer_id = customer_id
        self.contract_price = contract_price


class ContractEq:
    def __init__(
        self,
        contract_number: int,
        article: int,
        eq_price: float,
        amount: int
    ):
        self.contract_number = contract_number
        self.article = article
        self.eq_price = eq_price
        self.amount = amount


class Customer:
    def __init__(
        self,
        customer_id: int,
        customer_name: str,
        organ_phone_no: str,
        organ_email: str,
        post_address: str
    ):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.organ_phone_no = organ_phone_no
        self.organ_email = organ_email
        self.post_address = post_address

    def __str__(self) -> str:
        organ_phone_number = self.organ_phone_no if self.organ_phone_no != None else '~Undefined~'
        organ_email = self.organ_email if self.organ_email != None else '~Undefined~'
        post_address = self.post_address if self.post_address != None else '~Undefined~'
        result = (f"""*Name:* {self.customer_name}\n"""+
            f"""*Phone number:* {organ_phone_number}\n"""+
            f"""*Email:* {organ_email}\n"""+
            f"""*Address:* {post_address}\n""")
        return prepare_to_markdown(escape_italic(result))


class Employee:
    def __init__(
        self,
        employee_id: int = 0,
        emp_position: int = 0,
        emp_name: str = None,
        emp_login: str = None,
        emp_password: str = ''
    ):
        self.employee_id = employee_id
        self.emp_position = emp_position
        self.emp_name = emp_name
        self.emp_login = emp_login
        self.emp_password = emp_password

    def __str__(self) -> str:
        result = (f"""*Full name:* {self.emp_name}\n"""+
                f"""*Login:* {self.emp_login}""")
        return prepare_to_markdown(result)


class PriorClassifier:
    def __init__(
        self,
        priority_code: int,
        priority_name: str
    ):
        self.priority_code = priority_code
        self.priority_name = priority_name


class Task:
    def __init__(
        self,
        task_id=0,
        task_name='',
        creating_date='2022-01-01',
        closing_date=None,
        exec_period=-1,
        author_id=-1,
        executor_id=-1,
        customer_id=-1,
        task_type_id=-1,
        priority_code=-1,
        task_completed=False
    ):
        self.task_id = task_id
        self.task_name = task_name
        self.creating_date = creating_date
        self.closing_date = closing_date
        self.exec_period = exec_period
        self.author_id = author_id
        self.executor_id = executor_id
        self.customer_id = customer_id
        self.task_type_id = task_type_id
        self.priority_code = priority_code
        self.task_completed = task_completed


class TaskTypeClassifier:
    def __init__(
        self,
        task_type_id: int,
        task_type_name: str
    ):
        self.task_type_id = task_type_id
        self.task_type_name = task_type_name

    def __str__(self) -> str:
        result = f"""{self.task_type_name}"""
        return result

class Equipment:
    def __init__(
        self,
        article: int,
        equipment_name: str
    ):
        self.article = article
        self.equipment_name = equipment_name

    def __str__(self) -> str:
        result = (f"""*Article:* {self.article}\n"""+
        f"""*Name:* {self.equipment_name}""")
        return prepare_to_markdown(result)

        

def prepare_to_markdown(t: str) -> str:
    t = t.replace('-', '\-').replace('.', '\.').\
        replace('+', '\+').\
        replace('(', '\(').replace(')', '\)').\
        replace('<', '\<').replace('>', '\>')
    return t

def escape_italic(t: str) -> str:
    t = t.replace('_', '\_')
    return t