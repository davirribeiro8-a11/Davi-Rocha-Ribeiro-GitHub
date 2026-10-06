from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class Produto(CrudBase):

    table = "produto"

    fields = [
        "nome",
        "marca",
        "data_de_validade",
        "especificacao",
        "unidade_medida"
    ]

    def __init__(
        self,
        nome,
        marca,
        data_de_validade,
        especificacao,
        unidade_medida,
        quantidade=0
    ):
        self.nome = nome.strip()
        self.marca = marca.strip()
        self.data_de_validade = data_de_validade
        self.especificacao = especificacao.strip()
        self.unidade_medida = unidade_medida.strip()
        self.quantidade = int(quantidade)

    def validate(self):
        erros = [
            Validator.required(self.nome, "Nome"),
            Validator.min_length(self.nome, "Nome", 3),
            Validator.required(self.marca, "Marca"),
            Validator.min_length(self.marca, "Marca", 2),
            Validator.required(self.data_de_validade, "Data de validade"),
            Validator.date(self.data_de_validade, "Data de validade"),
            Validator.required(self.especificacao, "Especificação"),
            Validator.min_length(self.especificacao, "Especificação", 5),
            Validator.required(self.unidade_medida, "Unidade de medida"),
            Validator.non_negative(self.quantidade, "Quantidade"),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_all(cls, order_by="nome ASC"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"""
                SELECT
                    p.*,
                    COALESCE((
                        SELECT SUM(
                            CASE
                                WHEN m.tipo_movimentacao IN ('SAIDA', 'SAÍDA')
                                    THEN -m.quantidade
                                ELSE m.quantidade
                            END
                        )
                        FROM movimentacao m
                        WHERE m.produto_id = p.id
                    ), 0) AS quantidade
                FROM produto p
                ORDER BY {order_by}
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_all_com_localizacao(cls):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT
                    p.*,
                    l.rua,
                    l.numero,
                    l.andar,
                    COALESCE((
                        SELECT SUM(
                            CASE
                                WHEN m.tipo_movimentacao IN ('SAIDA', 'SAÍDA')
                                    THEN -m.quantidade
                                ELSE m.quantidade
                            END
                        )
                        FROM movimentacao m
                        WHERE m.produto_id = p.id
                    ), 0) AS quantidade
                FROM produto p
                LEFT JOIN localizacao l
                    ON l.id = p.localizacao_id
                ORDER BY p.nome
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_nome(cls, nome):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT *
                FROM produto
                WHERE nome LIKE %s
                ORDER BY nome ASC
            """
            cursor.execute(sql, (f"%{nome}%",))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def quantidade_em_estoque(cls, produto_id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                SELECT COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_movimentacao IN ('SAIDA', 'SAÍDA')
                                THEN -quantidade
                            ELSE quantidade
                        END
                    ), 0
                )
                FROM movimentacao
                WHERE produto_id = %s
            """
            cursor.execute(sql, (produto_id,))
            return int(cursor.fetchone()[0] or 0)
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def aumentar_estoque(cls, produto_id, quantidade):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                INSERT INTO movimentacao
                    (tipo_movimentacao, data_movimentacao, quantidade, produto_id)
                VALUES
                    ('ENTRADA', NOW(), %s, %s)
            """
            cursor.execute(sql, (quantidade, produto_id))
            conexao.commit()
            return cursor.lastrowid
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def diminuir_estoque(cls, produto_id, quantidade):
        estoque = cls.quantidade_em_estoque(produto_id)
        if quantidade > estoque:
            return 0

        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                INSERT INTO movimentacao
                    (tipo_movimentacao, data_movimentacao, quantidade, produto_id)
                VALUES
                    ('SAIDA', NOW(), %s, %s)
            """
            cursor.execute(sql, (quantidade, produto_id))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, produto_id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                SELECT COUNT(*)
                FROM movimentacao
                WHERE produto_id = %s
            """
            cursor.execute(sql, (produto_id,))
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, produto_id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            # =========================================================
            # 1. Verificar se o produto existe
            # =========================================================
            cursor.execute(
                """
                SELECT id
                FROM produto
                WHERE id = %s
                """,
                (produto_id,)
            )
            produto = cursor.fetchone()
            if not produto:
                raise ValueError("Produto não encontrado.")
            # =========================================================
            # 2. Buscar todas as movimentações do produto
            # =========================================================
            cursor.execute(
                """
                SELECT id
                FROM movimentacao
                WHERE produto_id = %s
                """,
                (produto_id,)
            )
            movimentacoes = cursor.fetchall()
            # Extrai os IDs
            movimentacao_ids = [
                movimentacao[0]
                for movimentacao in movimentacoes
            ]
            # =========================================================
            # 3. Excluir itens de entrada
            # =========================================================
            if movimentacao_ids:
                placeholders = ",".join(
                    ["%s"] * len(movimentacao_ids)
                )
                cursor.execute(
                    f"""
                    DELETE FROM item_entrada
                    WHERE movimentacao_id IN ({placeholders})
                    """,
                    tuple(movimentacao_ids)
                )
                # =====================================================
                # 4. Excluir itens de saída
                # =====================================================
                cursor.execute(
                    f"""
                    DELETE FROM item_saida
                    WHERE movimentacao_id IN ({placeholders})
                    """,
                    tuple(movimentacao_ids)
                )
            # =========================================================
            # 5. Excluir movimentações do produto
            # =========================================================
            cursor.execute(
                """
                DELETE FROM movimentacao
                WHERE produto_id = %s
                """,
                (produto_id,)
            )
            # =========================================================
            # 6. Excluir o produto
            # =========================================================
            cursor.execute(
                """
                DELETE FROM produto
                WHERE id = %s
                """,
                (produto_id,)
            )
            # =========================================================
            # 7. Confirmar tudo
            # =========================================================
            conexao.commit()
            return True
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()
