from models.crud_base import CrudBase
from core.database import conectar
import base64


class ProdutoModel(CrudBase):
    def __init__(self):
        super().__init__(
            tabela="produto",
            chave_primaria="id_produto",
            campos=[
                "codigo",
                "nome",
                "descricao",
                "unidade_medida",
                "estoque_minimo",
                "estoque_maximo",
                "status",
                "imagem_nome",
                "imagem_tipo",
                "imagem_blob"
            ]
        )

    def listar_com_imagem(self):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT 
                id_produto,
                codigo,
                nome,
                descricao,
                unidade_medida,
                estoque_minimo,
                estoque_maximo,
                status,
                imagem_nome,
                imagem_tipo,
                imagem_blob
            FROM produto
            ORDER BY nome
        """

        cursor.execute(sql)
        produtos = cursor.fetchall()

        cursor.close()
        conexao.close()

        for produto in produtos:
            produto["imagem_base64"] = None

            if produto["imagem_blob"]:
                imagem_base64 = base64.b64encode(produto["imagem_blob"]).decode("utf-8")
                produto["imagem_base64"] = imagem_base64

        return produtos

    def buscar_por_id_com_imagem(self, id_produto):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT 
                id_produto,
                codigo,
                nome,
                descricao,
                unidade_medida,
                estoque_minimo,
                estoque_maximo,
                status,
                imagem_nome,
                imagem_tipo,
                imagem_blob
            FROM produto
            WHERE id_produto = %s
        """

        cursor.execute(sql, (id_produto,))
        produto = cursor.fetchone()

        cursor.close()
        conexao.close()

        if produto and produto["imagem_blob"]:
            produto["imagem_base64"] = base64.b64encode(
                produto["imagem_blob"]
            ).decode("utf-8")
        elif produto:
            produto["imagem_base64"] = None

        return produto