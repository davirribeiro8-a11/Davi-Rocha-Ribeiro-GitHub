from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from datetime import timedelta
from functools import wraps
import time
from mysql.connector import IntegrityError
from database import connect

app = Flask(__name__)
app.secret_key = "chave-secreta-forte"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=20)
MODALIDADES = ["Musculação", "Natação", "Dança", "Luta"]

def query(sql, params=(), mode="all"):
    db = connect()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        result = cur.fetchone() if mode == "one" else cur.fetchall() if mode == "all" else None
        if mode == "write":
            db.commit()
        return result
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
        flash("Sessão encerrada por 20 minutos de inatividade.", "warning")
        return redirect(url_for("login"))
    session["last"] = now

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("usuario", "").strip()
        p = request.form.get("senha", "")
        row = query("SELECT * FROM usuarios WHERE usuario=%s", (u,), "one")
        if row and check_password_hash(row["senha"], p):
            session.clear()
            session.permanent = True
            session["uid"], session["nome"], session["last"] = row["id_usuario"], row["nome"], time.time()
            return redirect(url_for("home"))
        flash("Usuário ou senha inválidos.", "danger")
    return render_template("login.html")

@app.post("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "success")
    return redirect(url_for("login"))

@app.route("/")
@required
def home():
    totals = {k: query(f"SELECT COUNT(*) n FROM {t}", mode="one")["n"]
              for k, t in [("alunos","alunos"),("professores","professores"),("atividades","atividades")]}
    rows = query("""SELECT a.data_inicio,a.modalidade,al.nome aluno,p.nome professor
                    FROM atividades a JOIN alunos al ON al.id_aluno=a.id_aluno
                    JOIN professores p ON p.id_professor=a.id_professor
                    ORDER BY a.data_inicio LIMIT 5""")
    return render_template("index.html", totals=totals, rows=rows)

@app.route("/alunos")
@required
def alunos():
    term = request.args.get("q", "").strip()
    rows = query("SELECT * FROM alunos WHERE nome LIKE %s ORDER BY nome", (f"%{term}%",))
    return render_template("alunos.html", rows=rows, term=term)

@app.route("/alunos/novo", methods=["GET","POST"])
@app.route("/alunos/<int:id>/editar", methods=["GET","POST"])
@required
def aluno_form(id=None):
    row = query("SELECT * FROM alunos WHERE id_aluno=%s", (id,), "one") if id else None
    if id and not row:
        flash("Aluno não encontrado.", "warning"); return redirect(url_for("alunos"))
    if request.method == "POST":
        nome=request.form.get("nome","").strip()
        try:
            idade=int(request.form.get("idade",""))
            if not nome or idade < 0: raise ValueError
        except ValueError:
            flash("Informe nome e idade válida.", "danger")
            return render_template("form_aluno.html", row=row)
        data=(nome, idade, request.form.get("telefone","").strip(), request.form.get("cidade","").strip())
        if id:
            query("UPDATE alunos SET nome=%s,idade=%s,telefone=%s,cidade=%s WHERE id_aluno=%s", data+(id,), "write")
        else:
            query("INSERT INTO alunos (nome,idade,telefone,cidade) VALUES (%s,%s,%s,%s)", data, "write")
        flash("Aluno salvo.", "success"); return redirect(url_for("alunos"))
    return render_template("form_aluno.html", row=row)

@app.post("/alunos/<int:id>/excluir")
@required
def aluno_delete(id):
    try:
        query("DELETE FROM alunos WHERE id_aluno=%s", (id,), "write")
        flash("Aluno excluído.", "success")
    except IntegrityError:
        flash("Não é possível excluir aluno com atividades vinculadas.", "danger")
    return redirect(url_for("alunos"))

@app.route("/professores")
@required
def professores():
    return render_template("professores.html", rows=query("SELECT * FROM professores ORDER BY nome"))

@app.route("/professores/novo", methods=["GET","POST"])
@app.route("/professores/<int:id>/editar", methods=["GET","POST"])
@required
def professor_form(id=None):
    row=query("SELECT * FROM professores WHERE id_professor=%s",(id,),"one") if id else None
    if id and not row:
        flash("Professor não encontrado.", "warning"); return redirect(url_for("professores"))
    if request.method=="POST":
        nome=request.form.get("nome","").strip()
        esp=request.form.get("especialidade","")
        if not nome or esp not in MODALIDADES:
            flash("Informe nome e especialidade válida.", "danger")
            return render_template("form_professor.html", row=row, modalidades=MODALIDADES)
        data=(nome,request.form.get("telefone","").strip(),esp)
        if id: query("UPDATE professores SET nome=%s,telefone=%s,especialidade=%s WHERE id_professor=%s",data+(id,),"write")
        else: query("INSERT INTO professores (nome,telefone,especialidade) VALUES (%s,%s,%s)",data,"write")
        flash("Professor salvo.", "success"); return redirect(url_for("professores"))
    return render_template("form_professor.html", row=row, modalidades=MODALIDADES)

@app.post("/professores/<int:id>/excluir")
@required
def professor_delete(id):
    try:
        query("DELETE FROM professores WHERE id_professor=%s",(id,),"write")
        flash("Professor excluído.", "success")
    except IntegrityError:
        flash("Não é possível excluir professor vinculado a atividades.", "danger")
    return redirect(url_for("professores"))

@app.route("/atividades")
@required
def atividades():
    rows=query("""SELECT a.*,al.nome aluno,al.idade,p.nome professor,p.especialidade
      FROM atividades a JOIN alunos al ON al.id_aluno=a.id_aluno
      JOIN professores p ON p.id_professor=a.id_professor ORDER BY a.data_inicio""")
    return render_template("atividades.html", rows=rows)

@app.route("/atividades/nova", methods=["GET","POST"])
@app.route("/atividades/<int:id>/editar", methods=["GET","POST"])
@required
def atividade_form(id=None):
    row=query("SELECT * FROM atividades WHERE id_atividade=%s",(id,),"one") if id else None
    alunos=query("SELECT * FROM alunos ORDER BY nome")
    professores=query("SELECT * FROM professores ORDER BY nome")
    if request.method=="POST":
        try:
            aid=int(request.form["id_aluno"]); pid=int(request.form["id_professor"])
            modalidade=request.form["modalidade"]; valor=float(request.form["valor_mensal"])
            data=request.form["data_inicio"]
            if modalidade not in MODALIDADES or valor < 0 or not data: raise ValueError
            if not query("SELECT id_aluno FROM alunos WHERE id_aluno=%s",(aid,),"one"): raise ValueError
            if not query("SELECT id_professor FROM professores WHERE id_professor=%s",(pid,),"one"): raise ValueError
        except (ValueError, KeyError):
            flash("Confira todos os campos da atividade.", "danger")
            return render_template("form_atividade.html", row=row, alunos=alunos, professores=professores, modalidades=MODALIDADES)
        data_tuple=(aid,pid,modalidade,valor,data)
        if id: query("UPDATE atividades SET id_aluno=%s,id_professor=%s,modalidade=%s,valor_mensal=%s,data_inicio=%s WHERE id_atividade=%s",data_tuple+(id,),"write")
        else: query("INSERT INTO atividades (id_aluno,id_professor,modalidade,valor_mensal,data_inicio) VALUES (%s,%s,%s,%s,%s)",data_tuple,"write")
        flash("Atividade salva.", "success"); return redirect(url_for("atividades"))
    return render_template("form_atividade.html", row=row, alunos=alunos, professores=professores, modalidades=MODALIDADES)

@app.post("/atividades/<int:id>/excluir")
@required
def atividade_delete(id):
    query("DELETE FROM atividades WHERE id_atividade=%s",(id,),"write")
    flash("Atividade excluída.", "success")
    return redirect(url_for("atividades"))

@app.errorhandler(Exception)
def handle_error(error):
    # Mantém a mensagem amigável; confira o terminal para detalhes técnicos.
    app.logger.exception("Erro inesperado: %s", error)
    return render_template("erro.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
