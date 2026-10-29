from core.database import conectar


class PedidoEntradaModel:
    """
    Classe específica para pedido de entrada.

    Diferente de um CRUD comum, o pedido possui:
    - cabeçalho
    - vários itens
    - atualização automática do estoque
    """

    def listar(self):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT 
                pe.*,
                u.nome AS usuario
            FROM pedido_entrada pe
            INNER JOIN usuarios u 
                ON pe.id_usuario = u.id_usuario
            ORDER BY pe.id_pedido_entrada DESC
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        cursor.close()
        conexao.close()

        return dados

    def buscar_com_itens(self, id_pedido_entrada):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql_cabecalho = """
            SELECT 
                pe.*,
                u.nome AS usuario
            FROM pedido_entrada pe
            INNER JOIN usuarios u 
                ON pe.id_usuario = u.id_usuario
            WHERE pe.id_pedido_entrada = %s
        """

        cursor.execute(sql_cabecalho, (id_pedido_entrada,))
        cabecalho = cursor.fetchone()

        sql_itens = """
            SELECT 
                ipe.*,
                p.nome AS produto,
                p.codigo,
                l.nome AS localizacao
            FROM item_pedido_entrada ipe
            INNER JOIN produto p 
                ON ipe.id_produto = p.id_produto
            INNER JOIN localizacao l 
                ON ipe.id_localizacao = l.id_localizacao
            WHERE ipe.id_pedido_entrada = %s
        """

        cursor.execute(sql_itens, (id_pedido_entrada,))
        itens = cursor.fetchall()

        cursor.close()
        conexao.close()

        return {
            "cabecalho": cabecalho,
            "itens": itens
        }

    def inserir_com_itens(self, cabecalho, itens):
        conexao = conectar()
        cursor = conexao.cursor()

        try:
            sql_pedido = """
                INSERT INTO pedido_entrada
                (
                    numero_documento,
                    fornecedor,
                    data_entrada,
                    id_usuario,
                    observacao,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            valores_pedido = (
                cabecalho["numero_documento"],
                cabecalho["fornecedor"],
                cabecalho["data_entrada"],
                cabecalho["id_usuario"],
                cabecalho.get("observacao"),
                cabecalho.get("status", "finalizado")
            )

            cursor.execute(sql_pedido, valores_pedido)
            id_pedido_entrada = cursor.lastrowid

            for item in itens:
                quantidade = float(item["quantidade"])
                valor_unitario = float(item.get("valor_unitario", 0))
                valor_total = quantidade * valor_unitario

                sql_item = """
                    INSERT INTO item_pedido_entrada
                    (
                        id_pedido_entrada,
                        id_produto,
                        id_localizacao,
                        quantidade,
                        valor_unitario,
                        valor_total
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                valores_item = (
                    id_pedido_entrada,
                    item["id_produto"],
                    item["id_localizacao"],
                    quantidade,
                    valor_unitario,
                    valor_total
                )

                cursor.execute(sql_item, valores_item)

                self._atualizar_estoque_entrada(
                    cursor,
                    item["id_produto"],
                    item["id_localizacao"],
                    quantidade
                )

            conexao.commit()

            return id_pedido_entrada

        except Exception as erro:
            conexao.rollback()
            raise erro

        finally:
            cursor.close()
            conexao.close()

    def _atualizar_estoque_entrada(self, cursor, id_produto, id_localizacao, quantidade):
        sql_busca = """
            SELECT quantidade_atual
            FROM estoque
            WHERE id_produto = %s
            AND id_localizacao = %s
        """

        cursor.execute(sql_busca, (id_produto, id_localizacao))
        estoque = cursor.fetchone()

        if estoque is None:
            sql_insert = """
                INSERT INTO estoque
                (
                    id_produto,
                    id_localizacao,
                    quantidade_atual
                )
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                sql_insert,
                (id_produto, id_localizacao, quantidade)
            )

        else:
            sql_update = """
                UPDATE estoque
                SET quantidade_atual = quantidade_atual + %s
                WHERE id_produto = %s
                AND id_localizacao = %s
            """

            cursor.execute(
                sql_update,
                (quantidade, id_produto, id_localizacao)
            )

    def atualizar_com_itens(self, id_pedido_entrada, cabecalho, itens):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        try:
            # 1. Buscar itens antigos
            sql_itens_antigos = """
                SELECT id_produto, id_localizacao, quantidade
                FROM item_pedido_entrada
                WHERE id_pedido_entrada = %s
            """

            cursor.execute(sql_itens_antigos, (id_pedido_entrada,))
            itens_antigos = cursor.fetchall()

            # 2. Remover do estoque as quantidades antigas
            for item_antigo in itens_antigos:
                sql_estorno = """
                    UPDATE estoque
                    SET quantidade_atual = quantidade_atual - %s
                    WHERE id_produto = %s
                    AND id_localizacao = %s
                """

                cursor.execute(
                    sql_estorno,
                    (
                        item_antigo["quantidade"],
                        item_antigo["id_produto"],
                        item_antigo["id_localizacao"]
                    )
                )

            # 3. Atualizar cabeçalho
            sql_update_pedido = """
                UPDATE pedido_entrada
                SET 
                    numero_documento = %s,
                    fornecedor = %s,
                    data_entrada = %s,
                    observacao = %s,
                    status = %s
                WHERE id_pedido_entrada = %s
            """

            valores_pedido = (
                cabecalho["numero_documento"],
                cabecalho["fornecedor"],
                cabecalho["data_entrada"],
                cabecalho.get("observacao"),
                cabecalho.get("status", "finalizado"),
                id_pedido_entrada
            )

            cursor.execute(sql_update_pedido, valores_pedido)

            # 4. Apagar itens antigos
            sql_delete_itens = """
                DELETE FROM item_pedido_entrada
                WHERE id_pedido_entrada = %s
            """

            cursor.execute(sql_delete_itens, (id_pedido_entrada,))

            # 5. Inserir novos itens e atualizar estoque
            for item in itens:
                quantidade = float(item["quantidade"])
                valor_unitario = float(item.get("valor_unitario", 0))
                valor_total = quantidade * valor_unitario

                sql_item = """
                    INSERT INTO item_pedido_entrada
                    (
                        id_pedido_entrada,
                        id_produto,
                        id_localizacao,
                        quantidade,
                        valor_unitario,
                        valor_total
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                valores_item = (
                    id_pedido_entrada,
                    item["id_produto"],
                    item["id_localizacao"],
                    quantidade,
                    valor_unitario,
                    valor_total
                )

                cursor.execute(sql_item, valores_item)

                self._atualizar_estoque_entrada(
                    cursor,
                    item["id_produto"],
                    item["id_localizacao"],
                    quantidade
                )

            conexao.commit()

        except Exception as erro:
            conexao.rollback()
            raise erro

        finally:
            cursor.close()
            conexao.close()
    
    def contar(self):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT COUNT(*) AS total
            FROM pedido_entrada
        """

        cursor.execute(sql)
        resultado = cursor.fetchone()

        cursor.close()
        conexao.close()

        return resultado["total"]