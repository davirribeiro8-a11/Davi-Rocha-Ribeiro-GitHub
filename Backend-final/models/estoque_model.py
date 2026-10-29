from models.crud_base import CrudBase
from core.database import conectar


class EstoqueModel(CrudBase):
    def __init__(self):
        super().__init__(
            tabela="estoque",
            chave_primaria="id_estoque",
            campos=[
                "id_produto",
                "id_localizacao",
                "quantidade_atual"
            ]
        )

    def listar_completo(self):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT 
                e.id_estoque,
                p.id_produto,
                p.nome AS produto,
                p.codigo,
                p.unidade_medida,
                l.id_localizacao,
                l.nome AS localizacao,
                l.setor,
                e.quantidade_atual,
                e.atualizado_em
            FROM estoque e
            INNER JOIN produto p 
                ON e.id_produto = p.id_produto
            INNER JOIN localizacao l 
                ON e.id_localizacao = l.id_localizacao
            ORDER BY p.nome
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        cursor.close()
        conexao.close()

        return dados
    def contar_itens_em_estoque(self):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT COUNT(*) AS total
            FROM estoque
            WHERE quantidade_atual > 0
        """

        cursor.execute(sql)
        resultado = cursor.fetchone()

        cursor.close()
        conexao.close()

        return resultado["total"]