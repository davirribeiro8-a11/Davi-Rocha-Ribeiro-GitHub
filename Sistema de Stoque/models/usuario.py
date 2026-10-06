from core.crud_base import CrudBase
from core.database import Database
from core.security import verificar_senha, gerar_hash_senha


class Usuario(CrudBase):

    table = "usuario"

    fields = [
        "nome",
        "email",
        "senha",
        "tipo",
        "identificacao"
    ]

    def __init__(
        self,
        nome,
        email,
        senha,
        tipo,
        identificacao
    ):
        self.nome = nome.strip()
        self.email = email.strip().lower()
        self.senha = senha.strip()
        self.tipo = tipo.strip()
        self.identificacao = identificacao.strip()

    def validate(self):
        erros = []

        if not self.nome:
            erros.append("O campo Nome é obrigatório.")
        if not self.email:
            erros.append("O campo E-mail é obrigatório.")
        if not self.senha:
            erros.append("O campo Senha é obrigatório.")
        if not self.tipo:
            erros.append("O campo Tipo é obrigatório.")
        if not self.identificacao:
            erros.append("O campo Identificação é obrigatório.")

        return erros

    def insert(self):
        self.senha = gerar_hash_senha(self.senha)
        return super().insert()

    def update(self, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            usuario_atual = self.find_by_id(id)
            if not usuario_atual:
                raise ValueError("Usuário não encontrado.")

            senha = self.senha
            if not senha:
                senha = usuario_atual["senha"]
            else:
                senha = gerar_hash_senha(senha)

            sql = """
                UPDATE usuario
                SET nome = %s,
                    email = %s,
                    senha = %s,
                    tipo = %s,
                    identificacao = %s
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (
                    self.nome,
                    self.email,
                    senha,
                    self.tipo,
                    self.identificacao,
                    id,
                )
            )

            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def validar_no_banco(
        cls,
        email,
        senha=None,
        identificacao=None
    ):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT id, nome, email, senha, tipo, identificacao
                FROM usuario
                WHERE email = %s
            """
            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()

            if not usuario:
                return {
                    "valido": False,
                    "mensagem": "E-mail ou usuário não encontrado.",
                    "usuario": None
                }

            if senha is not None:
                if not verificar_senha(senha, usuario["senha"]):
                    return {
                        "valido": False,
                        "mensagem": "Senha incorreta.",
                        "usuario": None
                    }

            if identificacao is not None:
                if str(identificacao).strip() != str(usuario["identificacao"]).strip():
                    return {
                        "valido": False,
                        "mensagem": "Identificação não corresponde ao usuário.",
                        "usuario": None
                    }

            return {
                "valido": True,
                "mensagem": "Dados validados com sucesso.",
                "usuario": usuario
            }
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def autenticar(cls, email, senha):
        resultado = cls.validar_no_banco(
            email=email,
            senha=senha
        )

        if resultado["valido"]:
            return resultado["usuario"]

        return None
