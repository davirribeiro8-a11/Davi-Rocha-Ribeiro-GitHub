from models.usuario_model import UsuarioModel

usuarios_model = UsuarioModel()

dados = {
    "nome": "Administrador",
    "email": "admin@sistema.com",
    "senha": "123456",
    "perfil": "Davi",
    "status": "ativo"
}

usuarios_model.inserir_usuario(dados)

print("Usuário administrador criado com sucesso.")

