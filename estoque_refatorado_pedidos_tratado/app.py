from flask import Flask, render_template, request, redirect, url_for, flash
from models.produto import Produto
from models.movimentacao import Movimentacao
from models.pedido_movimentacao import PedidoMovimentacao

app = Flask(__name__)
app.secret_key = "chave_secreta"


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_produto_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "descricao": request.form.get("descricao", "").strip(),
        "categoria": request.form.get("categoria", "").strip(),
        "unidade_medida": request.form.get("unidade_medida", "").strip(),
        "quantidade": to_int(request.form.get("quantidade")),
        "estoque_minimo": to_int(request.form.get("estoque_minimo")),
        "preco_custo": to_float(request.form.get("preco_custo")),
        "preco_venda": to_float(request.form.get("preco_venda"))
    }


def get_pedido_form():
    return {
        "produto_id": to_int(request.form.get("produto_id")),
        "tipo": request.form.get("tipo", "").strip().upper(),
        "quantidade": to_int(request.form.get("quantidade")),
        "observacao": request.form.get("observacao", "").strip()
    }


@app.route("/")
def index():
    produtos_baixo = Produto.low_stock()
    return render_template("index.html", produtos_baixo=produtos_baixo)


@app.route("/produtos")
def produtos():
    return render_template("produtos.html", produtos=Produto.find_all(order_by="nome"))


@app.route("/produto/novo")
def novo_produto():
    return render_template("formulario_produto.html", produto=None)


@app.route("/produto/salvar", methods=["POST"])
def salvar_produto():
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate()

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("formulario_produto.html", produto=dados)

    try:
        produto.insert()
        flash("Produto cadastrado com sucesso.", "sucesso")
        return redirect(url_for("produtos"))
    except Exception as e:
        flash(f"Erro ao cadastrar produto: {e}", "erro")
        return render_template("formulario_produto.html", produto=dados)


@app.route("/produto/editar/<int:id>")
def editar_produto(id):
    produto = Produto.find_by_id(id)
    if not produto:
        flash("Produto não encontrado.", "erro")
        return redirect(url_for("produtos"))
    return render_template("formulario_produto.html", produto=produto)


@app.route("/produto/atualizar/<int:id>", methods=["POST"])
def atualizar_produto(id):
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate()

    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("formulario_produto.html", produto=dados)

    try:
        if not Produto.find_by_id(id):
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("produtos"))

        produto.update(id)
        flash("Produto atualizado com sucesso.", "sucesso")
        return redirect(url_for("produtos"))
    except Exception as e:
        dados["id"] = id
        flash(f"Erro ao atualizar produto: {e}", "erro")
        return render_template("formulario_produto.html", produto=dados)


@app.route("/produto/excluir/<int:id>")
def excluir_produto(id):
    try:
        Produto.safe_delete(id)
        flash("Produto excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash(f"Erro ao excluir produto: {e}", "erro")
    return redirect(url_for("produtos"))


@app.route("/pedidos")
def pedidos():
    return render_template("pedidos.html", pedidos=PedidoMovimentacao.find_all_with_product())


@app.route("/pedido/novo/<tipo>/<int:produto_id>")
def novo_pedido(tipo, produto_id):
    produto = Produto.find_by_id(produto_id)
    tipo = tipo.upper()

    if not produto:
        flash("Produto não encontrado.", "erro")
        return redirect(url_for("produtos"))

    if tipo not in ["ENTRADA", "SAIDA"]:
        flash("Tipo de pedido inválido.", "erro")
        return redirect(url_for("produtos"))

    return render_template("formulario_pedido.html", produto=produto, tipo=tipo, pedido=None)


@app.route("/pedido/salvar", methods=["POST"])
def salvar_pedido():
    dados = get_pedido_form()
    produto = Produto.find_by_id(dados["produto_id"])
    pedido = PedidoMovimentacao(**dados)
    erros = pedido.validate()

    if not produto:
        flash("Produto não encontrado.", "erro")
        return redirect(url_for("produtos"))

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("formulario_pedido.html", produto=produto, tipo=dados["tipo"], pedido=dados)

    try:
        pedido.insert()
        flash("Pedido criado com sucesso.", "sucesso")
        return redirect(url_for("pedidos"))
    except Exception as e:
        flash(f"Erro ao criar pedido: {e}", "erro")
        return render_template("formulario_pedido.html", produto=produto, tipo=dados["tipo"], pedido=dados)


@app.route("/pedido/processar/<int:id>")
def processar_pedido(id):
    try:
        mensagem = PedidoMovimentacao.processar(id)
        flash(mensagem, "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash(f"Erro ao processar pedido: {e}", "erro")
    return redirect(url_for("pedidos"))


@app.route("/pedido/cancelar/<int:id>")
def cancelar_pedido(id):
    try:
        mensagem = PedidoMovimentacao.cancelar(id)
        flash(mensagem, "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash(f"Erro ao cancelar pedido: {e}", "erro")
    return redirect(url_for("pedidos"))


@app.route("/movimentacoes")
def movimentacoes():
    return render_template("movimentacoes.html", movimentacoes=Movimentacao.find_all_with_product())


if __name__ == "__main__":
    app.run(debug=True)
