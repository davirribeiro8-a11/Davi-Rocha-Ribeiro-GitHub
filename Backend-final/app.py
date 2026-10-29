from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from werkzeug.utils import secure_filename
from core.security import login_obrigatorio

from models.usuario_model import UsuarioModel
from models.produto_model import ProdutoModel
from models.localizacao_model import LocalizacaoModel
from models.estoque_model import EstoqueModel
from models.sensor_model import SensorModel
from models.pedido_entrada_model import PedidoEntradaModel
from models.pedido_saida_model import PedidoSaidaModel


app = Flask(__name__)
app.secret_key = "chave_secreta_do_sistema_estoque"


# ============================================================
# INSTÂNCIAS DOS MODELS
# ============================================================

usuarios_model = UsuarioModel()
produtos_model = ProdutoModel()
localizacoes_model = LocalizacaoModel()
estoque_model = EstoqueModel()
sensores_model = SensorModel()
pedido_entrada_model = PedidoEntradaModel()
pedido_saida_model = PedidoSaidaModel()


# ============================================================
# ROTAS PRINCIPAIS
# ============================================================

EXTENSOES_PERMITIDAS = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


def imagem_permitida(tipo_arquivo):
    return tipo_arquivo in EXTENSOES_PERMITIDAS


@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    total_produtos = produtos_model.contar()
    total_estoque = estoque_model.contar_itens_em_estoque()
    total_entradas = pedido_entrada_model.contar()
    total_saidas = pedido_saida_model.contar()
    total_usuarios = usuarios_model.contar()
    total_sensores = sensores_model.contar()

    return render_template(
        "dashboard.html",
        total_produtos=total_produtos,
        total_estoque=total_estoque,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        total_usuarios=total_usuarios,
        total_sensores=total_sensores
    )


# ============================================================
# LOGIN E LOGOUT
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = usuarios_model.autenticar(email, senha)

        if usuario:
            session["usuario_id"] = usuario["id_usuario"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_perfil"] = usuario["perfil"]

            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))


# ============================================================
# USUÁRIOS
# ============================================================

@app.route("/usuarios")
@login_obrigatorio
def listar_usuarios():
    usuarios = usuarios_model.listar()
    return render_template("usuarios/listar.html", usuarios=usuarios)


@app.route("/usuarios/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo_usuario():
    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome"),
            "email": request.form.get("email"),
            "senha": request.form.get("senha"),
            "perfil": request.form.get("perfil"),
            "status": request.form.get("status", "ativo")
        }

        usuarios_model.inserir_usuario(dados)

        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for("listar_usuarios"))

    return render_template("usuarios/form.html", usuario=None)


@app.route("/usuarios/editar/<int:id_usuario>", methods=["GET", "POST"])
@login_obrigatorio
def editar_usuario(id_usuario):
    usuario = usuarios_model.buscar_por_id(id_usuario)

    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome"),
            "email": request.form.get("email"),
            "senha": request.form.get("senha"),
            "perfil": request.form.get("perfil"),
            "status": request.form.get("status")
        }

        usuarios_model.atualizar_usuario(id_usuario, dados)

        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("listar_usuarios"))

    return render_template("usuarios/form.html", usuario=usuario)


@app.route("/usuarios/excluir/<int:id_usuario>")
@login_obrigatorio
def excluir_usuario(id_usuario):
    usuarios_model.excluir(id_usuario)

    flash("Usuário excluído com sucesso!", "success")
    return redirect(url_for("listar_usuarios"))


# ============================================================
# PRODUTOS
# ============================================================

@app.route("/produtos")
@login_obrigatorio
def listar_produtos():
    produtos = produtos_model.listar_com_imagem()
    return render_template("produtos/listar.html", produtos=produtos)


@app.route("/produtos/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo_produto():
    if request.method == "POST":
        arquivo = request.files.get("imagem")

        imagem_nome = None
        imagem_tipo = None
        imagem_blob = None

        if arquivo and arquivo.filename != "":
            if not imagem_permitida(arquivo.content_type):
                flash("Formato de imagem inválido. Use PNG, JPG, JPEG ou WEBP.", "danger")
                return redirect(url_for("novo_produto"))

            imagem_nome = arquivo.filename
            imagem_tipo = arquivo.content_type
            imagem_blob = arquivo.read()

        dados = {
            "codigo": request.form.get("codigo"),
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "unidade_medida": request.form.get("unidade_medida"),
            "estoque_minimo": request.form.get("estoque_minimo"),
            "estoque_maximo": request.form.get("estoque_maximo"),
            "status": request.form.get("status", "ativo"),
            "imagem_nome": imagem_nome,
            "imagem_tipo": imagem_tipo,
            "imagem_blob": imagem_blob
        }

        produtos_model.inserir(dados)

        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("listar_produtos"))

    return render_template("produtos/form.html", produto=None)

@app.route("/produtos/editar/<int:id_produto>", methods=["GET", "POST"])
@login_obrigatorio
def editar_produto(id_produto):
    produto = produtos_model.buscar_por_id_com_imagem(id_produto)

    if request.method == "POST":
        arquivo = request.files.get("imagem")

        imagem_nome = produto["imagem_nome"]
        imagem_tipo = produto["imagem_tipo"]
        imagem_blob = produto["imagem_blob"]

        if arquivo and arquivo.filename != "":
            if not imagem_permitida(arquivo.content_type):
                flash("Formato de imagem inválido. Use PNG, JPG, JPEG ou WEBP.", "danger")
                return redirect(url_for("editar_produto", id_produto=id_produto))

            imagem_nome = arquivo.filename
            imagem_tipo = arquivo.content_type
            imagem_blob = arquivo.read()

        dados = {
            "codigo": request.form.get("codigo"),
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "unidade_medida": request.form.get("unidade_medida"),
            "estoque_minimo": request.form.get("estoque_minimo"),
            "estoque_maximo": request.form.get("estoque_maximo"),
            "status": request.form.get("status"),
            "imagem_nome": imagem_nome,
            "imagem_tipo": imagem_tipo,
            "imagem_blob": imagem_blob
        }

        produtos_model.atualizar(id_produto, dados)

        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for("listar_produtos"))

    return render_template("produtos/form.html", produto=produto)


@app.route("/produtos/excluir/<int:id_produto>")
@login_obrigatorio
def excluir_produto(id_produto):
    produtos_model.excluir(id_produto)

    flash("Produto excluído com sucesso!", "success")
    return redirect(url_for("listar_produtos"))


# ============================================================
# LOCALIZAÇÕES
# ============================================================

@app.route("/localizacoes")
@login_obrigatorio
def listar_localizacoes():
    localizacoes = localizacoes_model.listar()
    return render_template("localizacoes/listar.html", localizacoes=localizacoes)


@app.route("/localizacoes/novo", methods=["GET", "POST"])
@login_obrigatorio
def nova_localizacao():
    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome"),
            "setor": request.form.get("setor"),
            "corredor": request.form.get("corredor"),
            "prateleira": request.form.get("prateleira"),
            "observacao": request.form.get("observacao")
        }

        localizacoes_model.inserir(dados)

        flash("Localização cadastrada com sucesso!", "success")
        return redirect(url_for("listar_localizacoes"))

    return render_template("localizacoes/form.html", localizacao=None)


@app.route("/localizacoes/editar/<int:id_localizacao>", methods=["GET", "POST"])
@login_obrigatorio
def editar_localizacao(id_localizacao):
    localizacao = localizacoes_model.buscar_por_id(id_localizacao)

    if request.method == "POST":
        dados = {
            "nome": request.form.get("nome"),
            "setor": request.form.get("setor"),
            "corredor": request.form.get("corredor"),
            "prateleira": request.form.get("prateleira"),
            "observacao": request.form.get("observacao")
        }

        localizacoes_model.atualizar(id_localizacao, dados)

        flash("Localização atualizada com sucesso!", "success")
        return redirect(url_for("listar_localizacoes"))

    return render_template("localizacoes/form.html", localizacao=localizacao)


@app.route("/localizacoes/excluir/<int:id_localizacao>")
@login_obrigatorio
def excluir_localizacao(id_localizacao):
    localizacoes_model.excluir(id_localizacao)

    flash("Localização excluída com sucesso!", "success")
    return redirect(url_for("listar_localizacoes"))


# ============================================================
# ESTOQUE
# ============================================================

@app.route("/estoque")
@login_obrigatorio
def listar_estoque():
    estoque = estoque_model.listar_completo()
    return render_template("estoque/listar.html", estoque=estoque)


# ============================================================
# SENSORES
# ============================================================

@app.route("/sensores")
@login_obrigatorio
def listar_sensores():
    sensores = sensores_model.listar()
    return render_template("sensores/listar.html", sensores=sensores)


@app.route("/sensores/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo_sensor():
    produtos = produtos_model.listar()
    localizacoes = localizacoes_model.listar()

    if request.method == "POST":
        id_produto = request.form.get("id_produto")

        if id_produto == "":
            id_produto = None

        dados = {
            "nome": request.form.get("nome"),
            "tipo_sensor": request.form.get("tipo_sensor"),
            "codigo_sensor": request.form.get("codigo_sensor"),
            "id_localizacao": request.form.get("id_localizacao"),
            "id_produto": id_produto,
            "status": request.form.get("status", "ativo")
        }

        sensores_model.inserir(dados)

        flash("Sensor cadastrado com sucesso!", "success")
        return redirect(url_for("listar_sensores"))

    return render_template(
        "sensores/form.html",
        sensor=None,
        produtos=produtos,
        localizacoes=localizacoes
    )


@app.route("/sensores/editar/<int:id_sensor>", methods=["GET", "POST"])
@login_obrigatorio
def editar_sensor(id_sensor):
    sensor = sensores_model.buscar_por_id(id_sensor)
    produtos = produtos_model.listar()
    localizacoes = localizacoes_model.listar()

    if request.method == "POST":
        id_produto = request.form.get("id_produto")

        if id_produto == "":
            id_produto = None

        dados = {
            "nome": request.form.get("nome"),
            "tipo_sensor": request.form.get("tipo_sensor"),
            "codigo_sensor": request.form.get("codigo_sensor"),
            "id_localizacao": request.form.get("id_localizacao"),
            "id_produto": id_produto,
            "status": request.form.get("status")
        }

        sensores_model.atualizar(id_sensor, dados)

        flash("Sensor atualizado com sucesso!", "success")
        return redirect(url_for("listar_sensores"))

    return render_template(
        "sensores/form.html",
        sensor=sensor,
        produtos=produtos,
        localizacoes=localizacoes
    )


@app.route("/sensores/excluir/<int:id_sensor>")
@login_obrigatorio
def excluir_sensor(id_sensor):
    sensores_model.excluir(id_sensor)

    flash("Sensor excluído com sucesso!", "success")
    return redirect(url_for("listar_sensores"))


# ============================================================
# PEDIDO DE ENTRADA
# Cabeçalho + itens na mesma tela
# ============================================================

@app.route("/pedidos-entrada")
@login_obrigatorio
def listar_pedidos_entrada():
    pedidos = pedido_entrada_model.listar()
    return render_template("pedidos_entrada/listar.html", pedidos=pedidos)


@app.route("/pedidos-entrada/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo_pedido_entrada():
    produtos = produtos_model.listar()
    localizacoes = localizacoes_model.listar()

    if request.method == "POST":
        cabecalho = {
            "numero_documento": request.form.get("numero_documento"),
            "fornecedor": request.form.get("fornecedor"),
            "data_entrada": request.form.get("data_entrada"),
            "id_usuario": session["usuario_id"],
            "observacao": request.form.get("observacao"),
            "status": "finalizado"
        }

        produtos_form = request.form.getlist("id_produto[]")
        localizacoes_form = request.form.getlist("id_localizacao[]")
        quantidades_form = request.form.getlist("quantidade[]")
        valores_form = request.form.getlist("valor_unitario[]")

        itens = []

        for i in range(len(produtos_form)):
            if produtos_form[i] and localizacoes_form[i] and quantidades_form[i]:
                item = {
                    "id_produto": produtos_form[i],
                    "id_localizacao": localizacoes_form[i],
                    "quantidade": quantidades_form[i],
                    "valor_unitario": valores_form[i]
                }

                itens.append(item)

        if len(itens) == 0:
            flash("Adicione pelo menos um item ao pedido.", "warning")
            return redirect(url_for("novo_pedido_entrada"))

        try:
            pedido_entrada_model.inserir_com_itens(cabecalho, itens)

            flash("Pedido de entrada cadastrado com sucesso!", "success")
            return redirect(url_for("listar_pedidos_entrada"))

        except Exception as erro:
            flash(f"Erro ao cadastrar pedido de entrada: {erro}", "danger")

    return render_template(
        "pedidos_entrada/form.html",
        produtos=produtos,
        localizacoes=localizacoes
    )


@app.route("/pedidos-entrada/visualizar/<int:id_pedido_entrada>")
@login_obrigatorio
def visualizar_pedido_entrada(id_pedido_entrada):
    pedido = pedido_entrada_model.buscar_com_itens(id_pedido_entrada)

    return render_template(
        "pedidos_entrada/visualizar.html",
        pedido=pedido
    )


# ============================================================
# PEDIDO DE SAÍDA
# Cabeçalho + itens na mesma tela
# ============================================================

@app.route("/pedidos-saida")
@login_obrigatorio
def listar_pedidos_saida():
    pedidos = pedido_saida_model.listar()
    return render_template("pedidos_saida/listar.html", pedidos=pedidos)


@app.route("/pedidos-saida/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo_pedido_saida():
    produtos = produtos_model.listar()
    localizacoes = localizacoes_model.listar()

    if request.method == "POST":
        cabecalho = {
            "numero_documento": request.form.get("numero_documento"),
            "solicitante": request.form.get("solicitante"),
            "data_saida": request.form.get("data_saida"),
            "id_usuario": session["usuario_id"],
            "observacao": request.form.get("observacao"),
            "status": "finalizado"
        }

        produtos_form = request.form.getlist("id_produto[]")
        localizacoes_form = request.form.getlist("id_localizacao[]")
        quantidades_form = request.form.getlist("quantidade[]")

        itens = []

        for i in range(len(produtos_form)):
            if produtos_form[i] and localizacoes_form[i] and quantidades_form[i]:
                item = {
                    "id_produto": produtos_form[i],
                    "id_localizacao": localizacoes_form[i],
                    "quantidade": quantidades_form[i]
                }

                itens.append(item)

        if len(itens) == 0:
            flash("Adicione pelo menos um item ao pedido.", "warning")
            return redirect(url_for("novo_pedido_saida"))

        try:
            pedido_saida_model.inserir_com_itens(cabecalho, itens)

            flash("Pedido de saída cadastrado com sucesso!", "success")
            return redirect(url_for("listar_pedidos_saida"))

        except Exception as erro:
            flash(f"Erro ao cadastrar pedido de saída: {erro}", "danger")

    return render_template(
        "pedidos_saida/form.html",
        produtos=produtos,
        localizacoes=localizacoes
    )


@app.route("/pedidos-saida/visualizar/<int:id_pedido_saida>")
@login_obrigatorio
def visualizar_pedido_saida(id_pedido_saida):
    pedido = pedido_saida_model.buscar_com_itens(id_pedido_saida)

    return render_template(
        "pedidos_saida/visualizar.html",
        pedido=pedido
    )


# ============================================================
# ENDPOINTS PARA MOBILE / API
# ============================================================

@app.route("/api/login", methods=["POST"])
def api_login():
    dados = request.get_json()

    email = dados.get("email")
    senha = dados.get("senha")

    usuario = usuarios_model.autenticar(email, senha)

    if usuario:
        return jsonify({
            "ok": True,
            "mensagem": "Login realizado com sucesso.",
            "usuario": {
                "id_usuario": usuario["id_usuario"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "perfil": usuario["perfil"]
            }
        })

    return jsonify({
        "ok": False,
        "mensagem": "E-mail ou senha inválidos."
    }), 401


@app.route("/api/produtos", methods=["GET"])
def api_listar_produtos():
    produtos = produtos_model.listar()

    return jsonify({
        "ok": True,
        "produtos": produtos
    })


@app.route("/api/estoque", methods=["GET"])
def api_listar_estoque():
    estoque = estoque_model.listar_completo()

    return jsonify({
        "ok": True,
        "estoque": estoque
    })


@app.route("/api/sensores/dados", methods=["POST"])
def api_registrar_dados_sensor():
    dados = request.get_json()

    sensores_model.registrar_dados_sensor(dados)

    return jsonify({
        "ok": True,
        "mensagem": "Dados do sensor registrados com sucesso."
    })


# ============================================================
# EXECUÇÃO
# ============================================================


@app.route("/pedidos-entrada/editar/<int:id_pedido_entrada>", methods=["GET", "POST"])
@login_obrigatorio
def editar_pedido_entrada(id_pedido_entrada):
    produtos = produtos_model.listar()
    localizacoes = localizacoes_model.listar()
    pedido = pedido_entrada_model.buscar_com_itens(id_pedido_entrada)

    if request.method == "POST":
        cabecalho = {
            "numero_documento": request.form.get("numero_documento"),
            "fornecedor": request.form.get("fornecedor"),
            "data_entrada": request.form.get("data_entrada"),
            "observacao": request.form.get("observacao"),
            "status": "finalizado"
        }

        produtos_form = request.form.getlist("id_produto[]")
        localizacoes_form = request.form.getlist("id_localizacao[]")
        quantidades_form = request.form.getlist("quantidade[]")
        valores_form = request.form.getlist("valor_unitario[]")

        itens = []

        for i in range(len(produtos_form)):
            if produtos_form[i] and localizacoes_form[i] and quantidades_form[i]:
                itens.append({
                    "id_produto": produtos_form[i],
                    "id_localizacao": localizacoes_form[i],
                    "quantidade": quantidades_form[i],
                    "valor_unitario": valores_form[i]
                })

        if len(itens) == 0:
            flash("Adicione pelo menos um item ao pedido.", "warning")
            return redirect(url_for("editar_pedido_entrada", id_pedido_entrada=id_pedido_entrada))

        try:
            pedido_entrada_model.atualizar_com_itens(
                id_pedido_entrada,
                cabecalho,
                itens
            )

            flash("Pedido de entrada atualizado com sucesso!", "success")
            return redirect(url_for("listar_pedidos_entrada"))

        except Exception as erro:
            flash(f"Erro ao atualizar pedido de entrada: {erro}", "danger")

    return render_template(
        "pedidos_entrada/form.html",
        produtos=produtos,
        localizacoes=localizacoes,
        pedido=pedido
    )


@app.route("/pedidos-saida/editar/<int:id_pedido_saida>", methods=["GET", "POST"])
@login_obrigatorio
def editar_pedido_saida(id_pedido_saida):
    produtos = produtos_model.listar()
    localizacoes = localizacoes_model.listar()
    pedido = pedido_saida_model.buscar_com_itens(id_pedido_saida)

    if request.method == "POST":
        cabecalho = {
            "numero_documento": request.form.get("numero_documento"),
            "solicitante": request.form.get("solicitante"),
            "data_saida": request.form.get("data_saida"),
            "observacao": request.form.get("observacao"),
            "status": "finalizado"
        }

        produtos_form = request.form.getlist("id_produto[]")
        localizacoes_form = request.form.getlist("id_localizacao[]")
        quantidades_form = request.form.getlist("quantidade[]")

        itens = []

        for i in range(len(produtos_form)):
            if produtos_form[i] and localizacoes_form[i] and quantidades_form[i]:
                itens.append({
                    "id_produto": produtos_form[i],
                    "id_localizacao": localizacoes_form[i],
                    "quantidade": quantidades_form[i]
                })

        if len(itens) == 0:
            flash("Adicione pelo menos um item ao pedido.", "warning")
            return redirect(url_for("editar_pedido_saida", id_pedido_saida=id_pedido_saida))

        try:
            pedido_saida_model.atualizar_com_itens(
                id_pedido_saida,
                cabecalho,
                itens
            )

            flash("Pedido de saída atualizado com sucesso!", "success")
            return redirect(url_for("listar_pedidos_saida"))

        except Exception as erro:
            flash(f"Erro ao atualizar pedido de saída: {erro}", "danger")

    return render_template(
        "pedidos_saida/form.html",
        produtos=produtos,
        localizacoes=localizacoes,
        pedido=pedido
    )

if __name__ == "__main__":
    app.run(debug=True)