from database import connect
from werkzeug.security import generate_password_hash

db = connect()
cur = db.cursor()

# Usuário administrador
cur.execute(
    "INSERT IGNORE INTO usuarios (nome, usuario, senha) VALUES (%s, %s, %s)",
    ("Administrador FitLife", "admin", generate_password_hash("FitLife@123"))
)

# Professores
professores = [
    ("Carlos Mendes", "11988881111", "Musculação"),
    ("Juliana Alves", "11988882222", "Natação"),
    ("Rafael Souza", "11988883333", "Dança"),
    ("Mariana Lima", "11988884444", "Luta")
]

for p in professores:
    cur.execute(
        "SELECT id_professor FROM professores WHERE nome = %s",
        (p[0],)
    )

    if not cur.fetchone():
        cur.execute(
            "INSERT INTO professores (nome, telefone, especialidade) VALUES (%s, %s, %s)",
            p
        )

# Alunos
alunos = [
    ("Pedro Santos", 16, "11977771111", "Campinas"),
    ("Ana Clara", 17, "11977772222", "Mogi Mirim"),
    ("Lucas Oliveira", 16, "11977773333", "Itapira"),
    ("Beatriz Costa", 18, "11977774444", "Campinas"),
    ("Gabriel Rocha", 17, "11977775555", "Conchal")
]

for a in alunos:
    cur.execute(
        "SELECT id_aluno FROM alunos WHERE nome = %s",
        (a[0],)
    )

    if not cur.fetchone():
        cur.execute(
            "INSERT INTO alunos (nome, idade, telefone, cidade) VALUES (%s, %s, %s, %s)",
            a
        )

# Atividades
atividades = [
    ("Pedro Santos", "Carlos Mendes", "Musculação", 120.00, "2026-10-01"),
    ("Ana Clara", "Juliana Alves", "Natação", 150.00, "2026-10-03"),
    ("Lucas Oliveira", "Rafael Souza", "Dança", 100.00, "2026-10-05"),
    ("Beatriz Costa", "Mariana Lima", "Luta", 130.00, "2026-10-07"),
    ("Gabriel Rocha", "Carlos Mendes", "Musculação", 120.00, "2026-10-10")
]

for atividade in atividades:
    nome_aluno, nome_professor, modalidade, valor, data_inicio = atividade

    cur.execute(
        "SELECT id_aluno FROM alunos WHERE nome = %s",
        (nome_aluno,)
    )
    aluno = cur.fetchone()

    cur.execute(
        "SELECT id_professor FROM professores WHERE nome = %s",
        (nome_professor,)
    )
    professor = cur.fetchone()

    if not aluno or not professor:
        continue

    # Evita duplicar a mesma atividade para o aluno
    cur.execute(
        """
        SELECT id_atividade
        FROM atividades
        WHERE id_aluno = %s
          AND id_professor = %s
          AND modalidade = %s
          AND data_inicio = %s
        """,
        (aluno[0], professor[0], modalidade, data_inicio)
    )

    if not cur.fetchone():
        cur.execute(
            """
            INSERT INTO atividades
                (id_aluno, id_professor, modalidade, valor_mensal, data_inicio)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (aluno[0], professor[0], modalidade, valor, data_inicio)
        )

db.commit()
cur.close()
db.close()

print("Dados criados com sucesso.")
print("Login: admin | Senha: FitLife@123")
