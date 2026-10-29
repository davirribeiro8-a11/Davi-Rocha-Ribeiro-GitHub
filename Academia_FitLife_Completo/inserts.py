"""Insere dados demonstrativos sem duplicar os registros principais."""
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet
from pathlib import Path
from database import connect
import re

BASE = Path(__file__).parent
INSTANCE = BASE / "instance"
INSTANCE.mkdir(exist_ok=True)
KEY_FILE = INSTANCE / "fernet.key"
key = KEY_FILE.read_bytes().strip() if KEY_FILE.exists() else Fernet.generate_key()
if not KEY_FILE.exists():
    KEY_FILE.write_bytes(key)
fernet = Fernet(key)

def cpf_enc(cpf):
    return fernet.encrypt(re.sub(r"\D", "", cpf).encode()).decode()

db = connect()
cur = db.cursor()
try:
    users = [
        ("Administrador FitLife", "admin", "FitLife@123"),
        ("Recepção FitLife", "recepcao", "Recepcao@123"),
        ("Gestor FitLife", "gestor", "Gestor@123"),
    ]
    for nome, usuario, senha in users:
        cur.execute("SELECT id_usuario FROM usuarios WHERE usuario=%s", (usuario,))
        if not cur.fetchone():
            cur.execute("INSERT INTO usuarios (nome,usuario,senha) VALUES (%s,%s,%s)",
                        (nome, usuario, generate_password_hash(senha)))

    teachers = [
        ("Carlos Mendes", "11988881111", "Musculação"),
        ("Juliana Alves", "11988882222", "Natação"),
        ("Rafael Souza", "11988883333", "Dança"),
        ("Mariana Lima", "11988884444", "Luta"),
    ]
    for item in teachers:
        cur.execute("SELECT id_professor FROM professores WHERE nome=%s", (item[0],))
        if not cur.fetchone():
            cur.execute("INSERT INTO professores (nome,telefone,especialidade) VALUES (%s,%s,%s)", item)

    students = [
        ("Pedro Santos", "529.982.247-25", 26, "11977771111", "Campinas"),
        ("Ana Clara", "111.444.777-35", 24, "11977772222", "Mogi Mirim"),
        ("Lucas Oliveira", "935.411.347-80", 29, "11977773333", "Itapira"),
        ("Beatriz Costa", "123.456.789-09", 31, "11977774444", "Campinas"),
        ("Gabriel Rocha", "987.654.321-00", 22, "11977775555", "Conchal"),
    ]
    student_ids = {}
    for nome, cpf, idade, telefone, cidade in students:
        cur.execute("SELECT id_aluno FROM alunos WHERE nome=%s", (nome,))
        found = cur.fetchone()
        if found:
            sid = found[0]
        else:
            cur.execute("INSERT INTO alunos (nome,cpf_criptografado,idade,telefone,cidade) VALUES (%s,%s,%s,%s,%s)",
                        (nome, cpf_enc(cpf), idade, telefone, cidade))
            sid = cur.lastrowid
        student_ids[nome] = sid

    plans = [
        ("Pedro Santos", "Musculação Base", "Treino de força três vezes por semana.", "Musculação", 120, "2026-10-01"),
        ("Ana Clara", "Natação Condicionamento", "Aulas de natação e resistência.", "Natação", 150, "2026-10-03"),
        ("Lucas Oliveira", "Dança Fitness", "Aulas de dança em grupo.", "Dança", 100, "2026-10-05"),
        ("Beatriz Costa", "Luta Funcional", "Treinamento de luta e condicionamento.", "Luta", 130, "2026-10-07"),
        ("Gabriel Rocha", "Musculação Avançada", "Plano de força e hipertrofia.", "Musculação", 140, "2026-10-10"),
    ]
    plan_ids = {}
    for aluno, nome, descricao, modalidade, valor, inicio in plans:
        aid = student_ids[aluno]
        cur.execute("SELECT id_plano FROM planos_treinamento WHERE id_aluno=%s AND nome_plano=%s", (aid,nome))
        found = cur.fetchone()
        if found:
            pid = found[0]
        else:
            cur.execute("""INSERT INTO planos_treinamento
                (id_aluno,nome_plano,descricao,modalidade,valor_mensal,data_inicio)
                VALUES (%s,%s,%s,%s,%s,%s)""", (aid,nome,descricao,modalidade,valor,inicio))
            pid = cur.lastrowid
        plan_ids[aluno] = pid

    appointments = [
        ("Pedro Santos", "Carlos Mendes", "2026-11-02 08:00:00", "Avaliação inicial"),
        ("Ana Clara", "Juliana Alves", "2026-11-02 09:30:00", "Aula de adaptação"),
        ("Lucas Oliveira", "Rafael Souza", "2026-11-03 10:00:00", "Primeira aula"),
        ("Beatriz Costa", "Mariana Lima", "2026-11-04 18:00:00", "Levar roupa adequada"),
        ("Gabriel Rocha", "Carlos Mendes", "2026-11-05 07:30:00", "Avaliação de treino"),
    ]
    for aluno, professor, data, obs in appointments:
        aid = student_ids[aluno]
        pid = plan_ids[aluno]
        cur.execute("""SELECT id_agendamento FROM agendamentos
            WHERE id_aluno=%s AND id_plano=%s AND data_agendamento=%s""", (aid,pid,data))
        if not cur.fetchone():
            cur.execute("SELECT id_professor FROM professores WHERE nome=%s", (professor,))
            pr = cur.fetchone()
            cur.execute("""INSERT INTO agendamentos
                (id_aluno,id_plano,id_professor,data_agendamento,observacao)
                VALUES (%s,%s,%s,%s,%s)""", (aid,pid,pr[0] if pr else None,data,obs))
    db.commit()
    print("Dados demonstrativos inseridos/verificados.")
    print("Logins de teste:")
    print("admin / FitLife@123")
    print("recepcao / Recepcao@123")
    print("gestor / Gestor@123")
except Exception:
    db.rollback()
    raise
finally:
    cur.close()
    db.close()
