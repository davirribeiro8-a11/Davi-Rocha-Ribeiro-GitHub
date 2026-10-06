from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class ItemEntrada(CrudBase):
    table = "item_entrada"

    fields = ["quantidade", "valor", "pedido_entrada_id", "movimentacao_id"]

    def __init__(self, quantidade, valor, pedido_entrada_id, movimentacao_id=None):
        # Converte valores com segurança prevenindo exceção caso venha None ou ""
        self.quantidade = int(quantidade) if str(quantidade).isdigit() else 0
        self.valor = float(valor) if valor else 0.0
        self.pedido_entrada_id = int(pedido_entrada_id) if str(pedido_entrada_id).isdigit() else None
        self.movimentacao_id = int(movimentacao_id) if movimentacao_id and str(movimentacao_id).isdigit() else None

    def validate(self):
        erros = [
            Validator.required(self.quantidade, "Quantidade"),
            Validator.required(self.valor, "Valor"),
            Validator.required(self.pedido_entrada_id, "Pedido"),
            Validator.required(self.movimentacao_id, "Movimentação"),
        ]
        return [e for e in erros if e]

    @classmethod
    def find_by_pedido(cls, pedido_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT
                    ie.id,
                    ie.quantidade,
                    ie.valor, 
                    p.nome AS produto
                FROM item_entrada ie
                INNER JOIN movimentacao m
                    ON ie.movimentacao_id = m.id
                INNER JOIN produto p
                    ON m.produto_id = p.id
                WHERE ie.pedido_entrada_id = %s
            """
            cursor.execute(sql, (pedido_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()