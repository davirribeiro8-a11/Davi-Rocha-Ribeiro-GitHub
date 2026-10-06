from datetime import datetime
from core.crud_base import CrudBase
from core.database import Database


class Movimentacao(CrudBase):

    table = "movimentacao"

    fields = [
        "tipo_movimentacao",
        "data_movimentacao",
        "quantidade",
        "produto_id"
    ]

    def __init__(
        self,
        produto_id,
        tipo_movimentacao,
        quantidade,
        data_movimentacao=None
    ):
        self.produto_id = int(produto_id)
        self.tipo_movimentacao = tipo_movimentacao
        self.quantidade = int(quantidade)
        self.data_movimentacao = data_movimentacao or datetime.now()

    @classmethod
    def find_all_with_product(cls):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:
            sql = """
                SELECT
                    m.id,
                    m.produto_id,
                    p.nome AS produto,
                    m.tipo_movimentacao,
                    m.quantidade,
                    m.data_movimentacao
                FROM movimentacao m
                INNER JOIN produto p
                    ON m.produto_id = p.id
                ORDER BY m.data_movimentacao DESC
            """

            cursor.execute(sql)
            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()