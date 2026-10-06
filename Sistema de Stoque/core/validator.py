import re
from datetime import datetime

class Validator:
    @staticmethod
    def required(value, field_name):
        if value is None or str(value).strip() == "":
            return f"O campo {field_name} é obrigatório."
        return None
    @staticmethod
    def non_negative(value, field_name):
        try:
            if float(value) < 0:
                return f"O campo {field_name} não pode ser negativo."
        except (TypeError, ValueError):
            return f"O campo {field_name} deve ser numérico."
        return None
    @staticmethod
    def positive(value, field_name):
        try:
            if int(value) <= 0:
                return f"O campo {field_name} deve ser maior que zero."
        except (TypeError, ValueError):
            return f"O campo {field_name} deve ser numérico."
        return None
    @staticmethod
    def integer(value, field_name):
        try:
            int(value)
        except (TypeError, ValueError):
            return f"O campo {field_name} deve ser um número inteiro."
        return None
    @staticmethod
    def min_value(value, field_name, minimum):
        try:
            if int(value) < minimum:
                return f"O campo {field_name} deve ser no mínimo {minimum}."
        except (TypeError, ValueError):
            return f"O campo {field_name} deve ser numérico."
        return None
    @staticmethod
    def min_length(value, field_name, size):
        if value is None or len(str(value).strip()) < size:
            return f"O campo {field_name} deve ter pelo menos {size} caracteres."
        return None
    @staticmethod
    def email(value):
        if value is None or str(value).strip() == "":
            return "O email é obrigatório."
        regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(regex, str(value).strip()):
            return "Email inválido."
        return None
    @staticmethod
    def cnpj(value):
        if value is None:
            return "CNPJ inválido."
        cnpj = ''.join(filter(str.isdigit, str(value)))
        if len(cnpj) != 14:
            return "CNPJ inválido."
        return None
    @staticmethod
    def only_letters(value, field_name):
        if value is None:
            return f"O campo {field_name} é obrigatório."
        if any(char.isdigit() for char in str(value)):
            return f"O campo {field_name} não pode conter números."
        return None
    @staticmethod
    def date(value, field_name):
        if value is None or str(value).strip() == "":
            return f"O campo {field_name} é obrigatório."
        try:
            datetime.strptime(str(value), "%Y-%m-%d")
        except ValueError:
            return f"O campo {field_name} possui uma data inválida."
        return None