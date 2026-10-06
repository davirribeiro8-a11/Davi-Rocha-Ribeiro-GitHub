from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, session, url_for, flash
from core.database import Database
from models.item_saida import ItemSaida
from models.localizacao import Localizacao
from models.pedido_saida import PedidoSaida
from models.produto import Produto
from models.movimentacao import Movimentacao
from models.pedido_entrada import PedidoEntrada
from models.cliente import Cliente
from models.usuario import Usuario
from core.permissoes import permissao_obrigatoria
from models.item_entrada import ItemEntrada
from core.security import login_obrigatorio

app = Flask(__name__)
app.secret_key = "chave_secreta"


@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    LIMITE_ESTOQUE_BAIXO = 10
    DIAS_ALERTA_VALIDADE = 30

    produtos = Produto.find_all()
    movimentacoes = Movimentacao.find_all_with_product()
    clientes = Cliente.find_all()

    hoje = date.today()
    limite_validade = hoje + timedelta(days=DIAS_ALERTA_VALIDADE)

    produtos_baixo = [
        p for p in produtos if int(p.get("quantidade") or 0) <= LIMITE_ESTOQUE_BAIXO
    ]

    produtos_vencendo = [
        p
        for p in produtos
        if p.get("data_de_validade")
        and hoje <= p["data_de_validade"] <= limite_validade
    ]

    entradas = sum(
        1
        for m in movimentacoes
        if (m.get("tipo_movimentacao") or "").upper() == "ENTRADA"
    )
    saidas = sum(
        1
        for m in movimentacoes
        if (m.get("tipo_movimentacao") or "").upper() == "SAIDA"
    )

    produtos_ordenados = sorted(
        produtos, key=lambda p: int(p.get("quantidade") or 0), reverse=True
    )[:8]

    return render_template(
        "index.html",
        total_produtos=len(produtos),
        total_clientes=len(clientes),
        total_movimentacoes=len(movimentacoes),
        produtos_baixo=produtos_baixo,
        produtos_vencendo=produtos_vencendo,
        entradas=entradas,
        saidas=saidas,
        movimentacoes_recentes=movimentacoes[:6],
        labels_estoque=[p["nome"] for p in produtos_ordenados],
        quantidades_estoque=[int(p.get("quantidade") or 0) for p in produtos_ordenados],
    )


# (Form Helpers)=====================================================================================
def get_cliente_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "senha": request.form.get("senha", "").strip(),
        "cnpj": request.form.get("cnpj", "").strip(),
    }


def get_produto_form():
    qtd_str = request.form.get("quantidade", "0").strip()
    return {
        "nome": request.form.get("nome", "").strip(),
        "marca": request.form.get("marca", "").strip(),
        "data_de_validade": request.form.get("data_de_validade", "").strip(),
        "especificacao": request.form.get("especificacao", "").strip(),
        "unidade_medida": request.form.get("unidade_medida", "").strip(),
        "quantidade": int(qtd_str) if qtd_str.isdigit() else 0,
    }


def get_pedido_entrada_form():
    id_usuario_str = request.form.get("id_usuario", "0").strip()
    return {
        "numero_documento": request.form.get("numero_documento", "").strip(),
        "fornecedor": request.form.get("fornecedor", "").strip(),
        "data_entrada": request.form.get("data_entrada", "").strip(),
        "id_usuario": int(id_usuario_str) if id_usuario_str.isdigit() else 0,
        "observacao": request.form.get("observacao", "").strip(),
        "status": request.form.get("status", "").strip(),
    }


def get_login_form():
    return {
        "email": request.form.get("email", "").strip(),
        "senha": request.form.get("senha", "").strip(),
    }

def get_pedido_saida_form():
    cliente_id_str = request.form.get("cliente_id", "0").strip()
    usuario_id_str = request.form.get("usuario_id", "0").strip()
    quantidade_str = request.form.get("quantidade", "0").strip()
    valor_str = request.form.get("valor", "0").strip()
    return {
        "tipo": request.form.get("tipo", "").strip(),
        "pagamento": request.form.get("pagamento", "").strip(),
        "quantidade": int(quantidade_str) if quantidade_str.isdigit() else 0,
        "valor": float(valor_str.replace(",", ".")) if valor_str else 0.0,
        "data_pagamento": request.form.get("data_pagamento", "").strip(),
        "cliente_id": int(cliente_id_str) if cliente_id_str.isdigit() else 0,
        "usuario_id": int(usuario_id_str) if usuario_id_str.isdigit() else 0,
    }

def get_usuario_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "senha": request.form.get("senha", "").strip(),
        "identificacao": request.form.get("identificacao", "").strip(),
        "tipo": request.form.get("tipo", "").strip(),
    }


# (Login)===========================================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        usuario = Usuario.autenticar(email, senha)
        if usuario:
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_tipo"] = usuario["tipo"]
            flash("Login realizado com sucesso!", "sucesso")
            return redirect(url_for("dashboard"))
        flash("E-mail ou senha inválidos.", "erro")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))


# (Permissões e Usuário)=============================================================================
PERMISSOES = {
    "adm": {
        "usuarios_ver",
        "usuarios_criar",
        "usuarios_editar",
        "usuarios_excluir",
        "clientes_ver",
        "clientes_criar",
        "clientes_editar",
        "clientes_excluir",
        "produtos_ver",
        "produtos_criar",
        "produtos_editar",
        "produtos_excluir",
        "estoque_ver",
        "estoque_editar",
        "pedido_entrada",
        "pedido_saida",
        "localizacoes_ver",
        "localizacoes_criar",
        "localizacoes_editar",
        "localizacoes_excluir",
    },
    "estoquista": {
        "clientes_ver",
        "produtos_ver",
        "produtos_criar",
        "produtos_editar",
        "estoque_ver",
        "estoque_editar",
        "pedido_entrada",
        "pedido_saida",
        "localizacoes_ver",
    },
    "consulta": {
        "clientes_ver",
        "produtos_ver",
        "estoque_ver",
        "localizacoes_ver",
    },
}


def obter_usuario_logado():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return None
    try:
        return Usuario.find_by_id(usuario_id)
    except Exception as e:
        print(f"Erro ao buscar usuário logado: {e}")
        return None


def tem_permissao(permissao):
    usuario = obter_usuario_logado()
    if not usuario:
        return False
    tipo = usuario.get("tipo")
    if tipo == "admin":
        tipo = "adm"
    return permissao in PERMISSOES.get(tipo, set())


@app.context_processor
def inject_permissoes():
    return {"usuario_logado": obter_usuario_logado(), "tem_permissao": tem_permissao}


# (Rotas Usuário)===================================================================================
@app.route("/usuarios", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_ver")
def listar_usuarios():
    try:
        usuarios = Usuario.find_all(order_by="id DESC")
        return render_template("usuario_lista.html", usuarios=usuarios)
    except Exception as e:
        print("ERRO AO LISTAR USUÁRIOS:", e)
        flash("Erro ao carregar usuários.", "erro")
        return render_template("usuario_lista.html", usuarios=[])


@app.route("/usuario/novo", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_criar")
def novo_usuario():
    return render_template("usuario.html", usuario={})


@app.route("/usuario/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_criar")
def salvar_usuario():
    dados = get_usuario_form()
    try:
        usuario = Usuario(**dados)
        usuario.insert()
        flash("Usuário cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_usuarios"))
    except Exception as e:
        print("ERRO AO CADASTRAR USUÁRIO:", e)
        flash("Erro ao cadastrar usuário.", "erro")
        return render_template("usuario.html", usuario=dados)


@app.route("/usuario/<int:id>/editar", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_editar")
def buscar_usuario(id):
    try:
        usuario = Usuario.find_by_id(id)
        if not usuario:
            flash("Usuário não encontrado.", "erro")
            return redirect(url_for("listar_usuarios"))
        return render_template("usuario.html", usuario=usuario)
    except Exception as e:
        print("ERRO AO BUSCAR USUÁRIO:", e)
        flash("Erro ao carregar usuário.", "erro")
        return redirect(url_for("listar_usuarios"))


@app.route("/usuario/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_editar")
def atualizar_usuario(id):
    dados = get_usuario_form()
    try:
        usuario_existente = Usuario.find_by_id(id)
        if not usuario_existente:
            flash("Usuário não encontrado.", "erro")
            return redirect(url_for("listar_usuarios"))

        usuario = Usuario(**dados)
        erros = []
        if not usuario.nome:
            erros.append("O campo Nome é obrigatório.")
        if not usuario.email:
            erros.append("O campo E-mail é obrigatório.")
        if not usuario.tipo:
            erros.append("O campo Tipo é obrigatório.")
        if not usuario.identificacao:
            erros.append("O campo Identificação é obrigatório.")

        if erros:
            for erro in erros:
                flash(erro, "erro")
            dados["id"] = id
            return render_template("usuario.html", usuario=dados)

        linhas_afetadas = usuario.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_usuario", id=id))

        flash("Usuário atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_usuarios"))
    except Exception as e:
        print("ERRO AO ATUALIZAR USUÁRIO:", e)
        flash("Erro ao atualizar usuário.", "erro")
        dados["id"] = id
        return render_template("usuario.html", usuario=dados)


@app.route("/usuario/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_excluir")
def excluir_usuario(id):
    try:
        usuario = Usuario.find_by_id(id)
        if not usuario:
            flash("Usuário não encontrado.", "erro")
            return redirect(url_for("listar_usuarios"))

        Usuario.delete(id)
        flash("Usuário excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        print("ERRO AO EXCLUIR USUÁRIO:", e)
        flash("Erro ao excluir usuário.", "erro")

    return redirect(url_for("listar_usuarios"))


# (Cliente)===========================================================================================
@app.route("/cliente/novo", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("clientes_criar")
def novo_cliente():
    return render_template("cliente.html", cliente={})


@app.route("/clientes", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("clientes_ver")
def listar_clientes():
    try:
        clientes = Cliente.find_all(order_by="id DESC")
        return render_template("cliente_lista.html", clientes=clientes)
    except Exception as e:
        flash("Erro ao carregar clientes.", "erro")
        return render_template("cliente_lista.html", clientes=[])


@app.route("/cliente/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("clientes_criar")
def salvar_cliente():
    dados = get_cliente_form()
    dados["email"] = dados["email"].lower().strip()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("cliente.html", cliente=cliente)
    try:
        cliente.insert()
        flash("Cliente cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_clientes"))
    except Exception as e:
        print("ERRO AO CADASTRAR CLIENTE:", e)
        flash("Erro ao cadastrar cliente.", "erro")
        return render_template("cliente.html", cliente=cliente)


@app.route("/cliente/<int:id>/editar", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("clientes_editar")
def buscar_cliente(id):
    try:
        cliente = Cliente.find_by_id(id)
        if not cliente:
            flash("Cliente não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))
        return render_template("cliente.html", cliente=cliente)
    except Exception as e:
        flash("Erro ao carregar cliente.", "erro")
        return redirect(url_for("listar_clientes"))


@app.route("/cliente/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("clientes_editar")
def atualizar_cliente(id):
    dados = get_cliente_form()
    dados["email"] = dados["email"].lower().strip()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("cliente.html", cliente=dados)
    try:
        cliente_existente = Cliente.find_by_id(id)
        if not cliente_existente:
            flash("Cliente não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))
        linhas_afetadas = cliente.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_cliente", id=id))
        flash("Cliente atualizado com sucesso.", "sucesso")
        return redirect(url_for("buscar_cliente", id=id))
    except Exception as e:
        flash("Erro ao atualizar cliente.", "erro")
        dados["id"] = id
        return render_template("cliente.html", cliente=dados)


@app.route("/cliente/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("clientes_excluir")
def excluir_cliente(id):
    try:
        cliente = Cliente.find_by_id(id)
        if not cliente:
            flash("Cliente não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))
        Cliente.safe_delete(id)
        flash("Cliente excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir cliente.", "erro")
    return redirect(url_for("listar_clientes"))


# (Produto)============================================================================================
@app.route("/produto/novo", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("produtos_criar")
def novo_produto():
    # Passando dicionário vazio em vez de None evita UndefinedError no Jinja2
    return render_template("produtos.html", produto={})


@app.route("/produtos", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("produtos_ver")
def listar_produtos():
    try:
        produtos = Produto.find_all(order_by="id DESC")
        return render_template("listar_produtos.html", produtos=produtos)
    except Exception as e:
        print(f"Erro ao carregar produtos: {e}")
        flash("Erro ao carregar produtos.", "erro")
        return render_template("listar_produtos.html", produtos=[])


@app.route("/produto/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("produtos_criar")
def salvar_produto():
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate() if hasattr(produto, "validate") else []

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("produtos.html", produto=produto)

    try:
        novo_id = produto.insert()
        qtd_inicial = dados.get("quantidade", 0)
        movimentacao = Movimentacao(
            produto_id=novo_id, tipo_movimentacao="CADASTRO", quantidade=qtd_inicial
        )
        movimentacao.insert()
        flash("Produto cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")
        flash("Erro ao cadastrar produto.", "erro")
        return render_template("produtos.html", produto=produto)


@app.route("/produto/<int:id>/editar", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("produtos_editar")
def buscar_produto(id):
    try:
        produto = Produto.find_by_id(id)
        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))
        return render_template("produtos.html", produto=produto)
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        flash("Erro ao carregar produto.", "erro")
        return redirect(url_for("listar_produtos"))


@app.route("/produto/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("produtos_editar")
def atualizar_produto(id):
    dados = get_produto_form()
    produto = Produto(**dados)

    if hasattr(produto, "id"):
        produto.id = id
    elif isinstance(produto, dict):
        produto["id"] = id

    erros = produto.validate() if hasattr(produto, "validate") else []

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("produtos.html", produto=produto)

    try:
        produto_existente = Produto.find_by_id(id)
        if not produto_existente:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))

        linhas_afetadas = produto.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "info")

        flash("Produto atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        flash("Erro ao atualizar produto.", "erro")
        return render_template("produtos.html", produto=produto)


@app.route("/produto/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("produtos_excluir")
def excluir_produto(id):
    try:
        produto = Produto.find_by_id(id)
        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))

        Produto.safe_delete(id)
        flash("Produto excluído com sucesso.", "sucesso")
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")
        flash("Erro ao excluir produto.", "erro")

    return redirect(url_for("listar_produtos"))


# (Movimentação)===========================================================================================
@app.route("/movimentacoes")
@login_obrigatorio
@permissao_obrigatoria("estoque_ver")
def movimentacoes():
    movimentacoes_list = Movimentacao.find_all_with_product()
    movimentacoes_entrada = PedidoEntrada.listar_movimentacoes()
    movimentacoes_saida = PedidoSaida.listar_movimentacoes()

    return render_template(
        "movimentacoes.html",
        movimentacoes=movimentacoes_list,
        movimentacoes_entrada=movimentacoes_entrada,
        movimentacoes_saida=movimentacoes_saida,
    )


# (PedidoEntrada)===========================================================================================
@app.route("/pedido_entrada/novo", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def novo_pedido_entrada():
    usuarios = Usuario.find_all(order_by="nome")
    return render_template("pedido_entrada.html", pedido_entrada={}, usuarios=usuarios)


@app.route("/pedido_entrada", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def listar_pedido_entrada():
    try:
        pedidos_entrada = PedidoEntrada.find_all(order_by="id_pedido_entrada DESC")
        return render_template(
            "pedido_entrada_lista.html", pedidos_entrada=pedidos_entrada
        )
    except Exception as e:
        print("ERRO:", e)
        flash("Erro ao carregar pedidos de entrada.", "erro")
        return render_template("pedido_entrada_lista.html", pedidos_entrada=[])


@app.route("/pedido_entrada/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def salvar_pedido_entrada():
    dados = get_pedido_entrada_form()
    pedido_entrada = PedidoEntrada(**dados)
    erros = pedido_entrada.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=pedido_entrada,
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )
    try:
        novo_id = pedido_entrada.insert()
        flash("Pedido de entrada cadastrado com sucesso.", "sucesso")
        return redirect(url_for("buscar_pedido_entrada", id=novo_id))
    except Exception as e:
        flash(f"Erro ao cadastrar pedido: {e}", "erro")
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=pedido_entrada,
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )


@app.route("/pedido_entrada/<int:id>/editar")
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def buscar_pedido_entrada(id):
    try:
        pedido_entrada = PedidoEntrada.find_by_id(id)
        if not pedido_entrada:
            flash("Pedido não encontrado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))
        usuarios = Usuario.find_all(order_by="nome")
        movimentacoes_list = Movimentacao.find_all_with_product()
        itens = ItemEntrada.find_by_pedido(id)
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=pedido_entrada,
            usuarios=usuarios,
            movimentacoes=movimentacoes_list,
            itens=itens,
        )
    except Exception as e:
        flash("Erro ao carregar pedido.", "erro")
        return redirect(url_for("listar_pedido_entrada"))


@app.route("/pedido_entrada/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def atualizar_pedido_entrada(id):
    dados = get_pedido_entrada_form()
    pedido_entrada = PedidoEntrada(**dados)
    erros = pedido_entrada.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=dados,
            usuarios=Usuario.find_all(order_by="nome"),
        )
    try:
        pedido_existente = PedidoEntrada.find_by_id(id)
        if not pedido_existente:
            flash("Pedido não encontrado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))
        linhas_afetadas = pedido_entrada.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_pedido_entrada", id=id))
        flash("Pedido atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_pedido_entrada"))
    except Exception:
        flash("Erro ao atualizar pedido.", "erro")
        dados["id"] = id
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=dados,
            usuarios=Usuario.find_all(order_by="nome"),
        )


@app.route("/pedido_entrada/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def excluir_pedido_entrada(id):
    try:
        pedido_entrada = PedidoEntrada.find_by_id(id)
        if not pedido_entrada:
            flash("Pedido de entrada não encontrado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))
        PedidoEntrada.safe_delete(id)
        flash("Pedido de entrada excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir pedido de entrada.", "erro")
    return redirect(url_for("listar_pedido_entrada"))


# (Item Entrada)
# ===========================================================================================

@app.route("/item_entrada/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def salvar_item_entrada():
    pedido_id = request.form.get("pedido_entrada_id", "").strip()
    produto_id = request.form.get("produto_id", "").strip()
    movimentacao_id = request.form.get("movimentacao_id", "").strip()
    qtd_str = request.form.get("quantidade", "0").strip()
    valor_str = request.form.get("valor", "0").strip().replace(",", ".")
    # =========================================================
    # Converter quantidade
    # =========================================================
    quantidade = int(qtd_str) if qtd_str.isdigit() else 0
    # =========================================================
    # Converter valor
    # =========================================================
    try:
        valor = float(valor_str)
    except ValueError:
        valor = 0.0
    # =========================================================
    # Verificar pedido e produto
    # =========================================================
    if not pedido_id:
        flash("Pedido é obrigatório.", "erro")
        return redirect(
            url_for("buscar_pedido_entrada", id=pedido_id)
        )
    if not produto_id:
        flash("Produto é obrigatório.", "erro")
        return redirect(
            url_for("buscar_pedido_entrada", id=pedido_id)
        )
    try:
        pedido_id = int(pedido_id)
        produto_id = int(produto_id)
        # =====================================================
        # Verificar quantidade
        # =====================================================
        if quantidade <= 0:
            flash("A quantidade deve ser maior que zero.", "erro")
            return redirect(
                url_for("buscar_pedido_entrada", id=pedido_id)
            )
        # =====================================================
        # Verificar valor
        # =====================================================
        if valor < 0:
            flash("O valor não pode ser negativo.", "erro")
            return redirect(
                url_for("buscar_pedido_entrada", id=pedido_id)
            )
        # =====================================================
        # Criar movimentação de ENTRADA
        # =====================================================
        if not movimentacao_id:
            mov = Movimentacao(
                produto_id=produto_id,
                tipo_movimentacao="ENTRADA",
                quantidade=quantidade,
            )
            movimentacao_id = mov.insert()
        else:
            movimentacao_id = int(movimentacao_id)
        # =====================================================
        # Agora criar o ItemEntrada
        # =====================================================
        item = ItemEntrada(
            quantidade=quantidade,
            valor=valor,
            pedido_entrada_id=pedido_id,
            movimentacao_id=movimentacao_id,
        )
        # =====================================================
        # Validar ItemEntrada
        # =====================================================
        erros = item.validate() if hasattr(item, "validate") else []
        if erros:
            for erro in erros:
                flash(erro, "erro")
            return redirect(
                url_for("buscar_pedido_entrada", id=pedido_id)
            )
        # =====================================================
        # Salvar item
        # =====================================================
        item.insert()
        flash("Item de entrada adicionado com sucesso.", "sucesso")
    except Exception as e:
        print("ERRO AO ADICIONAR ITEM DE ENTRADA:", e)
        flash(
            f"Erro ao adicionar item de entrada: {e}",
            "erro"
        )
    return redirect(
        url_for("buscar_pedido_entrada", id=pedido_id)
    )

# (Localização)===========================================================================================
@app.route("/localizacao/novo")
@login_obrigatorio
@permissao_obrigatoria("localizacoes_criar")
def nova_localizacao():
    produtos = Produto.find_all()
    return render_template("localizacao.html", produtos=produtos)


@app.route("/localizacao")
@login_obrigatorio
@permissao_obrigatoria("localizacoes_ver")
def listar_localizacao():
    localizacoes = Localizacao.find_all("id DESC")
    return render_template("listar_localizacao.html", localizacoes=localizacoes)


@app.route("/localizacao/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("localizacoes_criar")
def salvar_localizacao():
    localizacao = Localizacao(
        request.form.get("rua", ""),
        request.form.get("numero", ""),
        request.form.get("andar", ""),
    )
    erros = localizacao.validate() if hasattr(localizacao, "validate") else []
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return redirect(url_for("nova_localizacao"))
    try:
        localizacao_id = localizacao.insert()
        produto_id = request.form.get("produto_id")
        if produto_id:
            conexao = Database.connect()
            cursor = conexao.cursor()
            cursor.execute(
                """
                UPDATE produto
                SET localizacao_id = %s
                WHERE id = %s
                """,
                (localizacao_id, produto_id),
            )
            conexao.commit()
            cursor.close()
            conexao.close()
        flash("Localização cadastrada com sucesso.", "sucesso")
    except Exception as e:
        flash(f"Erro ao cadastrar localização: {e}", "erro")

    return redirect(url_for("listar_localizacao"))


# (Pedido de Saída)============================================================================================
@app.route("/pedido_saida/novo")
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def novo_pedido_saida():
    clientes = Cliente.find_all(order_by="nome")
    usuarios = Usuario.find_all(order_by="nome")
    produtos = (
        Produto.find_all_com_localizacao()
        if hasattr(Produto, "find_all_com_localizacao")
        else Produto.find_all()
    )
    return render_template(
        "pedido_saida.html",
        pedido_saida={},
        clientes=clientes,
        usuarios=usuarios,
        produtos=produtos,
        itens=[],
    )


@app.route("/pedido_saida", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def listar_pedido_saida():
    try:
        pedidos_saida = (
            PedidoSaida.listar_pedidos()
            if hasattr(PedidoSaida, "listar_pedidos")
            else PedidoSaida.find_all()
        )
        return render_template("pedido_saida_lista.html", pedidos_saida=pedidos_saida)
    except Exception as e:
        flash("Erro ao carregar pedidos de saída.", "erro")
        return render_template("pedido_saida_lista.html", pedidos_saida=[])


@app.route("/pedido_saida/<int:id>/editar")
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def buscar_pedido_saida(id):
    try:
        pedido_saida = PedidoSaida.find_by_id(id)
        if not pedido_saida:
            flash("Pedido de saída não encontrado.", "erro")
            return redirect(url_for("listar_pedido_saida"))
        clientes = Cliente.find_all(order_by="nome")
        usuarios = Usuario.find_all(order_by="nome")
        produtos = (
            Produto.find_all_com_localizacao()
            if hasattr(Produto, "find_all_com_localizacao")
            else Produto.find_all()
        )
        itens = (
            ItemSaida.find_by_pedido(id) if hasattr(ItemSaida, "find_by_pedido") else []
        )
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=clientes,
            usuarios=usuarios,
            produtos=produtos,
            itens=itens,
        )
    except Exception as e:
        flash("Erro ao carregar pedido.", "erro")
        return redirect(url_for("listar_pedido_saida"))


@app.route("/pedido_saida/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def salvar_pedido_saida():
    dados = get_pedido_saida_form()
    pedido_saida = PedidoSaida(**dados)
    erros = pedido_saida.validate() if hasattr(pedido_saida, "validate") else []
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=Cliente.find_all(order_by="nome"),
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )
    try:
        novo_id = pedido_saida.insert()
        flash("Pedido de saída cadastrado com sucesso.", "sucesso")
        return redirect(url_for("buscar_pedido_saida", id=novo_id))
    except Exception as e:
        flash(f"Erro ao cadastrar pedido: {e}", "erro")
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=Cliente.find_all(order_by="nome"),
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )


@app.route("/pedido_saida/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def atualizar_pedido_saida(id):
    dados = get_pedido_saida_form()
    pedido_saida = PedidoSaida(**dados)
    erros = pedido_saida.validate() if hasattr(pedido_saida, "validate") else []
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template(
            "pedido_saida.html",
            pedido_saida=dados,
            clientes=Cliente.find_all(order_by="nome"),
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )
    try:
        pedido_existente = PedidoSaida.find_by_id(id)
        if not pedido_existente:
            flash("Pedido de saída não encontrado.", "erro")
            return redirect(url_for("listar_pedido_saida"))

        linhas_afetadas = pedido_saida.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "info")

        flash("Pedido de saída atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_pedido_saida"))
    except Exception as e:
        flash(f"Erro ao atualizar pedido: {e}", "erro")
        dados["id"] = id
        return render_template(
            "pedido_saida.html",
            pedido_saida=dados,
            clientes=Cliente.find_all(order_by="nome"),
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )

@app.route("/api/produto/<int:id>", methods=["GET"])
@login_obrigatorio
def api_produto(id):
    produto = Produto.find_by_id(id)
    if not produto:
        return {"erro": "Produto não encontrado."}, 404
    produto["quantidade"] = Produto.quantidade_em_estoque(id)
    return produto

@app.route("/item_saida/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def salvar_item_saida():
    pedido_id = request.form.get("pedido_saida_id")
    produto_id = request.form.get("produto_id")
    qtd_str = request.form.get("quantidade", "0").strip()
    valor_str = request.form.get("valor", "0").strip().replace(",", ".")
    quantidade = int(qtd_str) if qtd_str.isdigit() else 0
    try:
        valor = float(valor_str)
    except ValueError:
        valor = 0.0
    # Verifica se pedido e produto foram informados
    if not pedido_id or not produto_id:
        flash("Pedido e produto são obrigatórios.", "erro")
        return redirect(
            url_for("buscar_pedido_saida", id=pedido_id)
        )
    try:
        pedido_id = int(pedido_id)
        produto_id = int(produto_id)
        # Verifica o estoque atual
        estoque = Produto.quantidade_em_estoque(produto_id)
        if quantidade > estoque:
            flash(
                f"Estoque insuficiente. Estoque atual: {estoque}.",
                "erro"
            )
            return redirect(
                url_for("buscar_pedido_saida", id=pedido_id)
            )
        # Cria a movimentação de saída
        mov = Movimentacao(
            produto_id=produto_id,
            tipo_movimentacao="SAIDA",
            quantidade=quantidade
        )
        movimentacao_id = mov.insert()
        # Cria o item de saída já com a movimentação
        item = ItemSaida(
            quantidade,
            valor,
            pedido_id,
            movimentacao_id
        )
        # Valida o item
        erros = item.validate() if hasattr(item, "validate") else []
        if erros:
            for erro in erros:
                flash(erro, "erro")
            return redirect(
                url_for("buscar_pedido_saida", id=pedido_id)
            )
        # Salva o item
        item.insert()
        flash("Item adicionado com sucesso.", "sucesso")
    except Exception as e:
        print("ERRO AO ADICIONAR ITEM DE SAÍDA:", e)
        flash(f"Erro ao adicionar item: {e}", "erro")
    return redirect(
        url_for("buscar_pedido_saida", id=pedido_id)
    )

@app.route("/pedido_saida/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def excluir_pedido_saida(id):
    try:
        pedido = PedidoSaida.find_by_id(id)
        if not pedido:
            flash("Pedido de saída não encontrado.", "erro")
            return redirect(url_for("listar_pedido_saida"))

        PedidoSaida.safe_delete(id)
        flash("Pedido de saída excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        print("ERRO AO EXCLUIR PEDIDO DE SAÍDA:", e)
        flash("Erro ao excluir pedido de saída.", "erro")

    return redirect(url_for("listar_pedido_saida"))


if __name__ == "__main__":
    app.run(debug=True)
