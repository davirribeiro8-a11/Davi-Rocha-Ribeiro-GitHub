# Academia FitLife — MVP

MVP didático de gestão de academia com Python, Flask, Jinja, HTML, CSS e MySQL.

## Recursos
- Login com senha armazenada por hash.
- Sessão encerrada após 20 minutos de inatividade.
- Painel com contagem de alunos, professores e atividades.
- CRUD de alunos, busca por nome, CRUD de professores e CRUD de atividades.
- Relacionamento de atividade com aluno e professor.
- Proteção para não excluir aluno/professor que tenha atividade vinculada.
- SQL parametrizado.

## Instalação
1. Abra `schema.sql` no MySQL Workbench e execute.
2. Em `database.py`, configure usuário e senha do MySQL.
3. No terminal, nesta pasta, execute:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python inserts.py
python app.py
```

4. Acesse `http://127.0.0.1:5000`.

Login inicial: `admin`  
Senha inicial: `FitLife@123`


## Estrutura
- `app.py`: rotas e regras da aplicação.
- `database.py`: conexão MySQL.
- `schema.sql`: tabelas e relacionamentos.
- `seed.py`: usuário e dados iniciais.
- `templates/`: páginas Jinja.
- `static/style.css`: visual responsivo.

## DER
- Um aluno pode ter várias atividades.
- Um professor pode orientar várias atividades.
- Cada atividade aponta para um aluno e um professor.

