from models.crud_base import CrudBase
from core.database import conectar
from core.security import gerar_hash_senha, verificar_senha


class UsuarioModel(CrudBase):
    def __init__(self):
        super().__init__(
            tabela="alunos",
            chave_primaria="id_alunos",
            campos=[
                "nome",
                "cpf_criptografado",
                "email",
                "telefone"
            ]
        )

    def inserir_alunos(self, dados):
        """
        Cadastra um usuário criptografando a senha com bcrypt.
        """
        senha_texto = dados.get("senha")
        dados["senha"] = gerar_hash_senha(senha_texto)

        return self.inserir(dados)

    def atualizar_alunos(self, id_alunos, dados):
        """
        Atualiza usuário.
        Caso venha uma nova senha, criptografa antes de salvar.
        """
        senha = dados.get("senha")

        if senha:
            dados["senha"] = gerar_hash_senha(senha)
        else:
            dados.pop("senha", None)

        self.atualizar(id_usuario, dados)

    def autenticar(self, email, senha):
        """
        Verifica se o usuário existe e se a senha está correta.
        """
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT *
            FROM usuarios
            WHERE email = %s
            AND status = 'ativo'
        """

        cursor.execute(sql, (email,))
        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

        if usuario is None:
            return None

        senha_banco = usuario["senha"]

        if verificar_senha(senha, senha_banco):
            return usuario

        return None