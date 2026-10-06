from functools import wraps

from flask import session, flash, redirect, url_for

from models.usuario import Usuario


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
    }
}


def tem_permissao(usuario, permissao=None):
    
    if permissao is None:
        permissao = usuario

        usuario_id = session.get("usuario_id")

        if not usuario_id:
            return False

        usuario = Usuario.find_by_id(usuario_id)

        if not usuario:
            return False

    # -------------------------------------------------
    # SEM USUÁRIO
    # -------------------------------------------------
    if not usuario:
        return False

    # -------------------------------------------------
    # PEGA O TIPO DO USUÁRIO
    # -------------------------------------------------
    if isinstance(usuario, dict):
        tipo = usuario.get("tipo")
    else:
        tipo = getattr(usuario, "tipo", None)

    # -------------------------------------------------
    # ADMINISTRADOR TEM TODAS AS PERMISSÕES
    # -------------------------------------------------
    if tipo == "adm":
        return True

    # -------------------------------------------------
    # VERIFICA A PERMISSÃO
    # -------------------------------------------------
    return permissao in PERMISSOES.get(tipo, set())


def permissao_obrigatoria(permissao):
    """
    Decorator utilizado nas rotas que precisam
    de uma determinada permissão.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            # -----------------------------------------
            # VERIFICA SE EXISTE USUÁRIO LOGADO
            # -----------------------------------------
            usuario_id = session.get("usuario_id")

            if not usuario_id:
                flash(
                    "Você precisa estar logado.",
                    "erro"
                )

                return redirect(url_for("login"))

            # -----------------------------------------
            # BUSCA O USUÁRIO LOGADO
            # -----------------------------------------
            usuario = Usuario.find_by_id(usuario_id)

            if not usuario:
                session.pop("usuario_id", None)

                flash(
                    "Usuário não encontrado.",
                    "erro"
                )

                return redirect(url_for("login"))

            # -----------------------------------------
            # VERIFICA A PERMISSÃO
            # -----------------------------------------
            if not tem_permissao(usuario, permissao):

                flash(
                    "Você não possui permissão para acessar essa função.",
                    "erro"
                )

                return redirect(url_for("dashboard"))

            return func(*args, **kwargs)

        return wrapper

    return decorator