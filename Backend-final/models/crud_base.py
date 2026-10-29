from core.database import conectar


class CrudBase:
    """
    Classe base para operações genéricas de CRUD.

    Essa classe pode ser reaproveitada por cadastros simples, como:
    - produto
    - localização
    - sensor
    - usuários

    Cada classe filha informa:
    - nome da tabela
    - chave primária
    - campos permitidos
    """

    def __init__(self, tabela, chave_primaria, campos):
        self.tabela = tabela
        self.chave_primaria = chave_primaria
        self.campos = campos

    def listar(self):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = f"SELECT * FROM {self.tabela}"
        cursor.execute(sql)

        dados = cursor.fetchall()

        cursor.close()
        conexao.close()

        return dados

    def buscar_por_id(self, id_registro):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = f"""
            SELECT *
            FROM {self.tabela}
            WHERE {self.chave_primaria} = %s
        """

        cursor.execute(sql, (id_registro,))
        registro = cursor.fetchone()

        cursor.close()
        conexao.close()

        return registro

    def inserir(self, dados):
        conexao = conectar()
        cursor = conexao.cursor()

        campos_validos = []
        valores = []

        for campo in self.campos:
            if campo in dados:
                campos_validos.append(campo)
                valores.append(dados[campo])

        colunas = ", ".join(campos_validos)
        marcadores = ", ".join(["%s"] * len(campos_validos))

        sql = f"""
            INSERT INTO {self.tabela} ({colunas})
            VALUES ({marcadores})
        """

        cursor.execute(sql, valores)
        conexao.commit()

        novo_id = cursor.lastrowid

        cursor.close()
        conexao.close()

        return novo_id

    def atualizar(self, id_registro, dados):
        conexao = conectar()
        cursor = conexao.cursor()

        campos_update = []
        valores = []

        for campo in self.campos:
            if campo in dados:
                campos_update.append(f"{campo} = %s")
                valores.append(dados[campo])

        valores.append(id_registro)

        sql = f"""
            UPDATE {self.tabela}
            SET {", ".join(campos_update)}
            WHERE {self.chave_primaria} = %s
        """

        cursor.execute(sql, valores)
        conexao.commit()

        cursor.close()
        conexao.close()

    def excluir(self, id_registro):
        conexao = conectar()
        cursor = conexao.cursor()

        sql = f"""
            DELETE FROM {self.tabela}
            WHERE {self.chave_primaria} = %s
        """

        cursor.execute(sql, (id_registro,))
        conexao.commit()

        cursor.close()
        conexao.close()

    def contar(self):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = f"SELECT COUNT(*) AS total FROM {self.tabela}"

        cursor.execute(sql)
        resultado = cursor.fetchone()

        cursor.close()
        conexao.close()

        return resultado["total"]