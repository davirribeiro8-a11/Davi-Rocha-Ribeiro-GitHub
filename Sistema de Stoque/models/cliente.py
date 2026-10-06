from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class Cliente(CrudBase):

    table = "cliente"

    fields = [
        "nome",
        "email",
        "senha",
        "cnpj"
    ]

    def __init__(self, nome, email, senha, cnpj):
        self.nome = nome.strip()
        self.email = email.strip().lower()
        self.senha = senha.strip()
        self.cnpj = cnpj.strip()

    def validate(self):
        erros = [
            Validator.required(self.nome, "Nome"),
            Validator.min_length(self.nome, "Nome", 3),
            Validator.only_letters(self.nome, "Nome"),
            Validator.required(self.email, "Email"),
            Validator.email(self.email),
            Validator.required(self.senha, "Senha"),
            Validator.min_length(self.senha, "Senha", 6),
            Validator.required(self.cnpj, "CNPJ"),
            Validator.cnpj(self.cnpj),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_by_nome(cls, nome):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT *
                FROM cliente
                WHERE nome LIKE %s
                ORDER BY nome
            """
            cursor.execute(sql, (f"%{nome}%",))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_email(cls, email):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT *
                FROM cliente
                WHERE email = %s
            """
            cursor.execute(sql, (email,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                SELECT COUNT(*)
                FROM pedido_saida
                WHERE cliente_id = %s
            """
            cursor.execute(sql, (id,))
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, id):
        cliente = cls.find_by_id(id)
        if not cliente:
            raise ValueError("Cliente não encontrado.")

        if cls.has_related_records(id):
            raise ValueError(
                "Não é possível excluir o cliente porque existem pedidos de saída vinculados."
            )

        return cls.delete(id)
