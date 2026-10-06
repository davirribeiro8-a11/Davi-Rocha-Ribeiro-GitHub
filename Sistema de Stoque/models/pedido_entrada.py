from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class PedidoEntrada(CrudBase):

    table = "pedido_entrada"
    pk = "id_pedido_entrada"

    fields = [
        "numero_documento",
        "fornecedor",
        "data_entrada",
        "id_usuario",
        "observacao",
        "status",
    ]

    def __init__(
        self,
        numero_documento,
        fornecedor,
        data_entrada,
        id_usuario,
        observacao,
        status
    ):
        self.numero_documento = numero_documento.strip()
        self.fornecedor = fornecedor.strip()
        self.data_entrada = data_entrada
        self.id_usuario = int(id_usuario)
        self.observacao = observacao.strip()
        self.status = status.strip()

    def validate(self):
        erros = [
            Validator.required(self.numero_documento, "Número do documento"),
            Validator.required(self.fornecedor, "Fornecedor"),
            Validator.required(self.data_entrada, "Data de entrada"),
            Validator.required(self.id_usuario, "Usuário"),
            Validator.required(self.status, "Status"),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def listar_movimentacoes(cls):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT
                    pe.id_pedido_entrada,
                    pe.numero_documento,
                    pe.fornecedor,
                    pe.data_entrada,
                    pe.observacao,
                    pe.status,
                    u.nome AS usuario
                FROM pedido_entrada pe
                LEFT JOIN usuario u
                    ON pe.id_usuario = u.id
                ORDER BY pe.data_entrada DESC, pe.id_pedido_entrada DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
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
                FROM item_entrada
                WHERE pedido_entrada_id = %s
            """
            cursor.execute(sql, (id,))
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, id):
        pedido = cls.find_by_id(id)
        if not pedido:
            raise ValueError("Pedido de entrada não encontrado.")

        if cls.has_related_records(id):
            raise ValueError(
                "Não é possível excluir o pedido porque existem itens vinculados."
            )

        return cls.delete(id)
