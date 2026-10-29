from core.database import conectar


class PedidoSaidaModel:
    """
    Classe específica para pedido de saída.

    O pedido de saída possui:
    - cabeçalho
    - vários itens
    - validação de saldo
    - baixa automática no estoque
    """

    def listar(self):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT 
                ps.*,
                u.nome AS usuario
            FROM pedido_saida ps
            INNER JOIN usuarios u 
                ON ps.id_usuario = u.id_usuario
            ORDER BY ps.id_pedido_saida DESC
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        cursor.close()
        conexao.close()

        return dados

    def buscar_com_itens(self, id_pedido_saida):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql_cabecalho = """
            SELECT 
                ps.*,
                u.nome AS usuario
            FROM pedido_saida ps
            INNER JOIN usuarios u 
                ON ps.id_usuario = u.id_usuario
            WHERE ps.id_pedido_saida = %s
        """

        cursor.execute(sql_cabecalho, (id_pedido_saida,))
        cabecalho = cursor.fetchone()

        sql_itens = """
            SELECT 
                ips.*,
                p.nome AS produto,
                p.codigo,
                l.nome AS localizacao
            FROM item_pedido_saida ips
            INNER JOIN produto p 
                ON ips.id_produto = p.id_produto
            INNER JOIN localizacao l 
                ON ips.id_localizacao = l.id_localizacao
            WHERE ips.id_pedido_saida = %s
        """

        cursor.execute(sql_itens, (id_pedido_saida,))
        itens = cursor.fetchall()

        cursor.close()
        conexao.close()

        return {
            "cabecalho": cabecalho,
            "itens": itens
        }

    def inserir_com_itens(self, cabecalho, itens):
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        try:
            sql_pedido = """
                INSERT INTO pedido_saida
                (
                    numero_documento,
                    solicitante,
                    data_saida,
                    id_usuario,
                    observacao,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            valores_pedido = (
                cabecalho["numero_documento"],
                cabecalho["solicitante"],
                cabecalho["data_saida"],
                cabecalho["id_usuario"],
                cabecalho.get("observacao"),
                cabecalho.get("status", "finalizado")
            )

            cursor.execute(sql_pedido, valores_pedido)
            id_pedido_saida = cursor.lastrowid

            for item in itens:
                quantidade = float(item["quantidade"])

                self._validar_saldo(
                    cursor,
                    item["id_produto"],
                    item["id_localizacao"],
                    quantidade
                )

                sql_item = """
                    INSERT INTO item_pedido_saida
                    (
                        id_pedido_saida,
                        id_produto,
                        id_localizacao,
                        quantidade
                    )
                    VALUES (%s, %s, %s, %s)
                """

                valores_item = (
                    id_pedido_saida,
                    item["id_produto"],
                    item["id_localizacao"],
                    quantidade
                )

                cursor.execute(sql_item, valores_item)

                self._atualizar_estoque_saida(
                    cursor,
                    item["id_produto"],
                    item["id_localizacao"],
                    quantidade
                )

            conexao.commit()

            return id_pedido_saida

        except Exception as erro:
            conexao.rollback()
            raise erro

        finally:
            cursor.close()
            conexao.close()

    def _validar_saldo(self, cursor, id_produto, id_localizacao, quantidade):
        sql = """
            SELECT quantidade_atual
            FROM estoque
            WHERE id_produto = %s
            AND id_localizacao = %s
        """

        cursor.execute(sql, (id_produto, id_localizacao))
        estoque = cursor.fetchone()

        if estoque is None:
            raise Exception("Produto não encontrado no estoque.")

        quantidade_atual = float(estoque["quantidade_atual"])

        if quantidade_atual < quantidade:
            raise Exception("Saldo insuficiente em estoque.")

    def _atualizar_estoque_saida(self, cursor, id_produto, id_localizacao, quantidade):
        sql = """
            UPDATE estoque
            SET quantidade_atual = quantidade_atual - %s
            WHERE id_produto = %s
            AND id_localizacao = %s
        """

        cursor.execute(
            sql,
            (quantidade, id_produto, id_localizacao)
        )

        def atualizar_com_itens(self, id_pedido_saida, cabecalho, itens):
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            try:
                # 1. Buscar itens antigos
                sql_itens_antigos = """
                    SELECT id_produto, id_localizacao, quantidade
                    FROM item_pedido_saida
                    WHERE id_pedido_saida = %s
                """

                cursor.execute(sql_itens_antigos, (id_pedido_saida,))
                itens_antigos = cursor.fetchall()

                # 2. Devolver ao estoque as quantidades antigas
                for item_antigo in itens_antigos:
                    sql_estorno = """
                        UPDATE estoque
                        SET quantidade_atual = quantidade_atual + %s
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
                    UPDATE pedido_saida
                    SET 
                        numero_documento = %s,
                        solicitante = %s,
                        data_saida = %s,
                        observacao = %s,
                        status = %s
                    WHERE id_pedido_saida = %s
                """

                valores_pedido = (
                    cabecalho["numero_documento"],
                    cabecalho["solicitante"],
                    cabecalho["data_saida"],
                    cabecalho.get("observacao"),
                    cabecalho.get("status", "finalizado"),
                    id_pedido_saida
                )

                cursor.execute(sql_update_pedido, valores_pedido)

                # 4. Apagar itens antigos
                sql_delete_itens = """
                    DELETE FROM item_pedido_saida
                    WHERE id_pedido_saida = %s
                """

                cursor.execute(sql_delete_itens, (id_pedido_saida,))

                # 5. Validar saldo dos novos itens
                for item in itens:
                    quantidade = float(item["quantidade"])

                    self._validar_saldo(
                        cursor,
                        item["id_produto"],
                        item["id_localizacao"],
                        quantidade
                    )

                # 6. Inserir novos itens e baixar estoque
                for item in itens:
                    quantidade = float(item["quantidade"])

                    sql_item = """
                        INSERT INTO item_pedido_saida
                        (
                            id_pedido_saida,
                            id_produto,
                            id_localizacao,
                            quantidade
                        )
                        VALUES (%s, %s, %s, %s)
                    """

                    valores_item = (
                        id_pedido_saida,
                        item["id_produto"],
                        item["id_localizacao"],
                        quantidade
                    )

                    cursor.execute(sql_item, valores_item)

                    self._atualizar_estoque_saida(
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
            FROM pedido_saida
        """

        cursor.execute(sql)
        resultado = cursor.fetchone()

        cursor.close()
        conexao.close()

        return resultado["total"]