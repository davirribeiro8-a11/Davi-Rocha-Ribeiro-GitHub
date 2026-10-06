from models.usuario import Usuario
from core.security import gerar_hash_senha

usuario = Usuario(
    nome="gerenciador admin",
    email="smartmedsproject@gmail.com",
    senha=gerar_hash_senha("123456"),
    tipo="admin",
    identificacao="0001",
)

usuario.insert()

print("Administrador criado com sucesso")
