from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from datetime import timedelta
from functools import wraps
from mysql.connector import IntegrityError
from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path
import os, time
from database import connect

app = Flask(__name__)
app.secret_key = os.getenv("FITLIFE_SECRET_KEY", "troque-esta-chave-antes-de-publicar-o-sistema")
app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=20),
    SESSION_REFRESH_EACH_REQUEST=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
MODALIDADES = ["Musculação", "Natação", "Dança", "Luta", "Condicionamento"]
INSTANCE = Path(__file__).parent / "instance"
INSTANCE.mkdir(exist_ok=True)
FERNET_PATH = INSTANCE / "fernet.key"
if os.getenv("FITLIFE_FERNET_KEY"):
    FERNET_KEY = os.environ["FITLIFE_FERNET_KEY"].encode()
elif FERNET_PATH.exists():
    FERNET_KEY = FERNET_PATH.read_bytes().strip()
else:
    FERNET_KEY = Fernet.generate_key()
    FERNET_PATH.write_bytes(FERNET_KEY)
    try:
        FERNET_PATH.chmod(0o600)
    except OSError:
        pass
fernet = Fernet(FERNET_KEY)

def encrypt_cpf(cpf):
    digits = "".join(c for c in cpf if c.isdigit())
    if len(digits) != 11:
        raise ValueError("O CPF deve conter 11 números.")
    return fernet.encrypt(digits.encode()).decode()

def decrypt_cpf(token):
    try:
        return fernet.decrypt(token.encode()).decode()
    except (InvalidToken, ValueError):
        return "Não disponível"

def query(sql, params=(), mode="all"):
    db = connect()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        if mode == "write":
            db.commit()
            return cur.lastrowid
        return cur.fetchone() if mode == "one" else cur.fetchall()
    except Exception:
        db.rollback()
        raise
    finally:
        cur.close()
        db.close()

def required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "uid" not in session:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.before_request
def session_timeout():
    if request.endpoint in (None, "login", "static") or "uid" not in session:
        return
    now = time.time()
    if now - session.get("last", now) > 1200:
        session.clear()
        flash("Sessão encerrada após 20 minutos de inatividade.", "warning")
        return redirect(url_for("login"))
    session["last"] = now

@app.route("/login", methods=["GET", "POST"])
def login():
    if "uid" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("usuario", "").strip()
        password = request.form.get("senha", "")
        user = query("SELECT * FROM usuarios WHERE usuario=%s", (username,), "one")
        if user and check_password_hash(user["senha"], password):
            session.clear()
            session.permanent = True
            session["uid"] = user["id_usuario"]
            session["nome"] = user["nome"]
            session["last"] = time.time()
            return redirect(url_for("home"))
        flash("Usuário ou senha inválidos.", "danger")
    return render_template("login.html")

@app.post("/logout")
@required
def logout():
    session.clear()
    flash("Você saiu do sistema.", "success")
    return redirect(url_for("login"))

@app.route("/")
@required
def home():
    totals = {
        "alunos": query("SELECT COUNT(*) n FROM alunos", mode="one")["n"],
        "planos": query("SELECT COUNT(*) n FROM planos_treinamento", mode="one")["n"],
        "agendamentos": query("SELECT COUNT(*) n FROM agendamentos", mode="one")["n"],
    }
    rows = query("""SELECT g.data_agendamento, al.nome aluno, p.nome_plano plano,
                    pr.nome professor
                    FROM agendamentos g
                    JOIN alunos al ON al.id_aluno=g.id_aluno
                    JOIN planos_treinamento p ON p.id_plano=g.id_plano
                    LEFT JOIN professores pr ON pr.id_professor=g.id_professor
                    ORDER BY g.data_agendamento LIMIT 8""")
    return render_template("index.html", totals=totals, rows=rows)

@app.route("/alunos")
@required
def alunos():
    term = request.args.get("q", "").strip()
    rows = query("""SELECT id_aluno,nome,idade,telefone,cidade
                    FROM alunos WHERE nome LIKE %s OR telefone LIKE %s OR cidade LIKE %s
                    ORDER BY nome""", (f"%{term}%",)*3)
    return render_template("alunos.html", rows=rows, term=term)

@app.route("/alunos/novo", methods=["GET","POST"])
@app.route("/alunos/<int:id>/editar", methods=["GET","POST"])
@required
def aluno_form(id=None):
    row = query("SELECT * FROM alunos WHERE id_aluno=%s", (id,), "one") if id else None
    if id and not row:
        flash("Aluno não encontrado.", "warning")
        return redirect(url_for("alunos"))
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        cpf = request.form.get("cpf", "").strip()
        try:
            idade = int(request.form.get("idade", ""))
            if not nome or idade < 0:
                raise ValueError
            encrypted = encrypt_cpf(cpf) if cpf else (row["cpf_criptografado"] if row else None)
            if not encrypted:
                raise ValueError
        except ValueError:
            flash("Informe nome, idade válida e CPF com 11 dígitos. Na edição, deixe CPF vazio para mantê-lo.", "danger")
            return render_template("form_aluno.html", row=row)
        data = (nome, encrypted, idade, request.form.get("telefone","").strip(), request.form.get("cidade","").strip())
        if id:
            query("UPDATE alunos SET nome=%s,cpf_criptografado=%s,idade=%s,telefone=%s,cidade=%s WHERE id_aluno=%s", data+(id,), "write")
        else:
            query("INSERT INTO alunos (nome,cpf_criptografado,idade,telefone,cidade) VALUES (%s,%s,%s,%s,%s)", data, "write")
        flash("Aluno salvo com sucesso.", "success")
        return redirect(url_for("alunos"))
    return render_template("form_aluno.html", row=row)

@app.post("/alunos/<int:id>/excluir")
@required
def aluno_delete(id):
    try:
        query("DELETE FROM alunos WHERE id_aluno=%s", (id,), "write")
        flash("Aluno excluído.", "success")
    except IntegrityError:
        flash("Não é possível excluir aluno vinculado a plano ou agendamento.", "danger")
    return redirect(url_for("alunos"))

@app.route("/professores")
@required
def professores():
    rows = query("SELECT * FROM professores ORDER BY nome")
    return render_template("professores.html", rows=rows)

@app.route("/professores/novo", methods=["GET","POST"])
@app.route("/professores/<int:id>/editar", methods=["GET","POST"])
@required
def professor_form(id=None):
    row = query("SELECT * FROM professores WHERE id_professor=%s", (id,), "one") if id else None
    if id and not row:
        flash("Professor não encontrado.", "warning")
        return redirect(url_for("professores"))
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        esp = request.form.get("especialidade", "")
        if not nome or esp not in MODALIDADES:
            flash("Informe nome e especialidade válida.", "danger")
            return render_template("form_professor.html", row=row, modalidades=MODALIDADES)
        data = (nome, request.form.get("telefone","").strip(), esp)
        if id:
            query("UPDATE professores SET nome=%s,telefone=%s,especialidade=%s WHERE id_professor=%s", data+(id,), "write")
        else:
            query("INSERT INTO professores (nome,telefone,especialidade) VALUES (%s,%s,%s)", data, "write")
        flash("Professor salvo.", "success")
        return redirect(url_for("professores"))
    return render_template("form_professor.html", row=row, modalidades=MODALIDADES)

@app.post("/professores/<int:id>/excluir")
@required
def professor_delete(id):
    try:
        query("DELETE FROM professores WHERE id_professor=%s", (id,), "write")
        flash("Professor excluído.", "success")
    except IntegrityError:
        flash("Professor vinculado a agendamento não pode ser excluído.", "danger")
    return redirect(url_for("professores"))

@app.route("/planos")
@required
def planos():
    rows = query("""SELECT p.*, a.nome aluno FROM planos_treinamento p
                    JOIN alunos a ON a.id_aluno=p.id_aluno
                    ORDER BY p.nome_plano""")
    return render_template("planos.html", rows=rows)

@app.route("/planos/novo", methods=["GET","POST"])
@app.route("/planos/<int:id>/editar", methods=["GET","POST"])
@required
def plano_form(id=None):
    row = query("SELECT * FROM planos_treinamento WHERE id_plano=%s", (id,), "one") if id else None
    alunos = query("SELECT id_aluno,nome FROM alunos ORDER BY nome")
    if id and not row:
        flash("Plano não encontrado.", "warning")
        return redirect(url_for("planos"))
    if request.method == "POST":
        try:
            aid = int(request.form["id_aluno"])
            nome = request.form.get("nome_plano","").strip()
            modalidade = request.form.get("modalidade","")
            valor = float(request.form.get("valor_mensal",""))
            data = request.form.get("data_inicio","")
            descricao = request.form.get("descricao","").strip()
            if not nome or modalidade not in MODALIDADES or valor < 0 or not data:
                raise ValueError
            if not query("SELECT id_aluno FROM alunos WHERE id_aluno=%s", (aid,), "one"):
                raise ValueError
        except (ValueError, KeyError):
            flash("Confira os dados e selecione um aluno cadastrado.", "danger")
            return render_template("form_plano.html", row=row, alunos=alunos, modalidades=MODALIDADES)
        values = (aid,nome,descricao,modalidade,valor,data)
        if id:
            query("""UPDATE planos_treinamento SET id_aluno=%s,nome_plano=%s,descricao=%s,
                     modalidade=%s,valor_mensal=%s,data_inicio=%s WHERE id_plano=%s""", values+(id,), "write")
        else:
            query("""INSERT INTO planos_treinamento
                     (id_aluno,nome_plano,descricao,modalidade,valor_mensal,data_inicio)
                     VALUES (%s,%s,%s,%s,%s,%s)""", values, "write")
        flash("Plano salvo com sucesso.", "success")
        return redirect(url_for("planos"))
    return render_template("form_plano.html", row=row, alunos=alunos, modalidades=MODALIDADES)

@app.post("/planos/<int:id>/excluir")
@required
def plano_delete(id):
    try:
        query("DELETE FROM planos_treinamento WHERE id_plano=%s", (id,), "write")
        flash("Plano excluído.", "success")
    except IntegrityError:
        flash("Não é possível excluir plano com agendamentos vinculados.", "danger")
    return redirect(url_for("planos"))

@app.route("/agendamentos")
@required
def agendamentos():
    rows = query("""SELECT g.*, al.nome aluno, p.nome_plano plano, p.modalidade,
                    pr.nome professor FROM agendamentos g
                    JOIN alunos al ON al.id_aluno=g.id_aluno
                    JOIN planos_treinamento p ON p.id_plano=g.id_plano
                    LEFT JOIN professores pr ON pr.id_professor=g.id_professor
                    ORDER BY g.data_agendamento ASC""")
    return render_template("agendamentos.html", rows=rows)

@app.route("/agendamentos/novo", methods=["GET","POST"])
@app.route("/agendamentos/<int:id>/editar", methods=["GET","POST"])
@required
def agendamento_form(id=None):
    row = query("SELECT * FROM agendamentos WHERE id_agendamento=%s", (id,), "one") if id else None
    alunos = query("SELECT id_aluno,nome FROM alunos ORDER BY nome")
    planos = query("""SELECT p.id_plano,p.id_aluno,p.nome_plano,a.nome aluno
                      FROM planos_treinamento p JOIN alunos a ON a.id_aluno=p.id_aluno ORDER BY a.nome,p.nome_plano""")
    professores = query("SELECT id_professor,nome FROM professores ORDER BY nome")
    if id and not row:
        flash("Agendamento não encontrado.", "warning")
        return redirect(url_for("agendamentos"))
    if request.method == "POST":
        try:
            aid = int(request.form["id_aluno"])
            pid = int(request.form["id_plano"])
            professor_raw = request.form.get("id_professor","").strip()
            professor_id = int(professor_raw) if professor_raw else None
            data = request.form.get("data_agendamento","").strip().replace("T"," ")
            obs = request.form.get("observacao","").strip()
            if not data or not query("SELECT id_aluno FROM alunos WHERE id_aluno=%s", (aid,), "one"):
                raise ValueError
            plan = query("SELECT id_plano,id_aluno FROM planos_treinamento WHERE id_plano=%s", (pid,), "one")
            if not plan or plan["id_aluno"] != aid:
                raise ValueError
            if professor_id and not query("SELECT id_professor FROM professores WHERE id_professor=%s",(professor_id,),"one"):
                raise ValueError
        except (ValueError, KeyError):
            flash("Confira a data e selecione aluno, plano desse aluno e professor válido.", "danger")
            return render_template("form_agendamento.html", row=row, alunos=alunos, planos=planos, professores=professores)
        if len(data) == 16:
            data += ":00"
        values=(aid,pid,professor_id,data,obs)
        if id:
            query("""UPDATE agendamentos SET id_aluno=%s,id_plano=%s,id_professor=%s,
                     data_agendamento=%s,observacao=%s WHERE id_agendamento=%s""", values+(id,), "write")
        else:
            query("""INSERT INTO agendamentos (id_aluno,id_plano,id_professor,data_agendamento,observacao)
                     VALUES (%s,%s,%s,%s,%s)""", values, "write")
        flash("Agendamento salvo com sucesso.", "success")
        return redirect(url_for("agendamentos"))
    return render_template("form_agendamento.html", row=row, alunos=alunos, planos=planos, professores=professores)

@app.post("/agendamentos/<int:id>/excluir")
@required
def agendamento_delete(id):
    query("DELETE FROM agendamentos WHERE id_agendamento=%s", (id,), "write")
    flash("Agendamento excluído.", "success")
    return redirect(url_for("agendamentos"))

@app.errorhandler(404)
def not_found(error):
    return render_template("erro.html", mensagem="A página solicitada não foi encontrada."), 404

@app.errorhandler(Exception)
def handle_error(error):
    app.logger.exception("Erro inesperado: %s", error)
    return render_template("erro.html", mensagem="Ocorreu um erro inesperado. Confira a conexão com o banco e o terminal."), 500

if __name__ == "__main__":
    app.run(debug=True)
