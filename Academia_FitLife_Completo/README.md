# Academia FitLife — Sistema de gestão

Projeto educacional em Python, Flask, Jinja, HTML/CSS e MySQL, adaptado ao desafio de cadastro e gerenciamento de alunos, planos de treinamento e agendamentos.

## Funcionalidades
- Login com senha armazenada usando hash seguro.
- Sessão com encerramento após 20 minutos de inatividade.
- Tela principal com o nome do usuário logado, atalhos e próximos agendamentos.
- Cadastro, edição, exclusão protegida e busca de alunos.
- CPF criptografado com Fernet antes de ser gravado no banco.
- Cadastro e gerenciamento de planos vinculados a um aluno já cadastrado.
- Cadastro, listagem por data/hora, edição da data e exclusão de agendamentos.
- Cadastro de professores, opcionais para associar a um agendamento.
- Consultas SQL parametrizadas e validação de relacionamentos.
- Script de dados de demonstração com pelo menos três registros para cada tabela criada.

## Requisitos
- Python 3.10 ou superior.
- MySQL Server e MySQL Workbench.
- Pacotes listados em `requirements.txt`.

## Instalação no Windows
1. Extraia o ZIP e abra a pasta do projeto no VS Code.
2. No MySQL Workbench, execute o arquivo `schema.sql`. **Atenção:** este esquema foi atualizado e não altera automaticamente tabelas antigas criadas com o projeto original. Se você já tem dados no banco anterior, faça backup e planeje uma migração antes de substituir tabelas; para uma instalação de teste limpa, use um banco vazio.
3. Confira as credenciais em `database.py`. Por padrão: host `localhost`, usuário `root`, senha `123456`, banco `academia_fitlife`. É recomendável usar variáveis de ambiente para credenciais reais.
4. No terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python inserts.py
python app.py
```

5. Abra `http://127.0.0.1:5000`.

## Usuários de demonstração
- `admin` / `FitLife@123`
- `recepcao` / `Recepcao@123`
- `gestor` / `Gestor@123`

Troque as senhas e a `secret_key` antes de qualquer uso real.

## CPF criptografado
Na primeira execução, o sistema cria `instance/fernet.key`. A chave é necessária para descriptografar CPFs já armazenados. Mantenha-a fora do controle de versão, restrinja o acesso e faça backup seguro. Se perder a chave, os CPFs antigos não poderão ser recuperados. O CPF não é exibido nas listagens.

## Banco de dados e dados de teste
`schema.sql` cria cinco tabelas: `usuarios`, `alunos`, `professores`, `planos_treinamento` e `agendamentos`. `inserts.py` insere dados demonstrativos idempotentemente, sem repetir os registros principais quando executado mais de uma vez. CPFs de exemplo são fictícios e servem apenas para testes.

## Documentação
- `DOCUMENTACAO.md`: requisitos funcionais, regras de negócio e testes.
- `DER.md`: entidades, atributos e relacionamentos.
- `schema.sql`: script de criação do banco e tabelas.

## Observações
Projeto didático, não auditado para produção. Para publicar na internet, configure chaves secretas por ambiente, HTTPS, CSRF, controle de acesso por perfil, política de backup e revisão de segurança/LGPD.
