# Documentação técnica — Academia FitLife

## 1. Contextualização
A academia precisa substituir o controle manual de alunos, planos e horários por um sistema informatizado, reduzindo perdas de agendamento, duplicidade de informação e riscos de exposição de dados pessoais.

## 2. Objetivo geral
Desenvolver uma aplicação web que permita autenticação de usuários e gerenciamento centralizado de alunos, planos de treinamento e agendamentos, com persistência em MySQL e proteção do CPF.

## 3. Requisitos funcionais
- **RF01 — Autenticar usuário:** permitir login com usuário e senha válidos.
- **RF02 — Tratar falha de autenticação:** exibir mensagem amigável quando o login falhar.
- **RF03 — Encerrar sessão:** permitir logout manual e expirar a sessão após 20 minutos de inatividade.
- **RF04 — Exibir painel:** mostrar nome do usuário logado, resumo de registros, atalhos e próximos agendamentos.
- **RF05 — Cadastrar aluno:** registrar nome, CPF, idade, telefone e cidade.
- **RF06 — Proteger CPF:** criptografar o CPF antes de armazená-lo no banco.
- **RF07 — Buscar aluno:** aceitar termo de pesquisa e atualizar a listagem por nome, telefone ou cidade.
- **RF08 — Editar aluno:** permitir alterar dados de aluno e persistir no banco.
- **RF09 — Gerenciar professor:** cadastrar, listar, editar e excluir professores, impedindo exclusão quando houver agendamento vinculado.
- **RF10 — Cadastrar plano:** criar plano associado a aluno existente.
- **RF11 — Gerenciar planos:** listar, editar e excluir planos; impedir exclusão quando houver agendamento vinculado.
- **RF12 — Cadastrar agendamento:** selecionar aluno, plano desse aluno, data/hora e, opcionalmente, professor.
- **RF13 — Listar agendamentos:** exibir aluno e plano, ordenando por data/hora crescente.
- **RF14 — Editar agendamento:** permitir alterar data/hora e outros dados do agendamento e salvar no banco.
- **RF15 — Excluir agendamento:** permitir excluir um agendamento selecionado.
- **RF16 — Persistir dados:** salvar as alterações de cadastros no MySQL.

## 4. Requisitos não funcionais
- **RNF01 — Segurança de senha:** armazenar senhas com hash seguro, nunca em texto puro.
- **RNF02 — Segurança do CPF:** usar criptografia autenticada (Fernet) e manter a chave fora de repositórios públicos.
- **RNF03 — Integridade:** utilizar PK, FK e regras de exclusão restritiva para proteger relacionamentos.
- **RNF04 — Consultas seguras:** usar consultas SQL parametrizadas.
- **RNF05 — Manutenibilidade:** separar rotas, acesso ao banco, templates, estilos e scripts SQL.
- **RNF06 — Usabilidade:** apresentar mensagens de sucesso/erro e formulários com validação.
- **RNF07 — Sessão:** usar cookies HTTPOnly e SameSite e expiração por inatividade.

## 5. Regras de negócio
1. O script SQL cria cinco tabelas e o script `inserts.py` popula cada tabela com pelo menos três registros de demonstração.
2. Login inválido não concede acesso e apresenta mensagem de erro.
3. O CPF é criptografado antes da persistência.
4. O painel apresenta o nome do usuário autenticado, links para os recursos e opção de saída.
5. A busca de alunos atualiza a listagem após confirmação; a edição salva os dados no banco.
6. Agendamentos são listados em ordem crescente de data/hora e mostram aluno e plano; a edição salva a nova data.
7. Um plano precisa estar associado a um aluno previamente cadastrado.
8. Um agendamento deve associar o mesmo aluno selecionado ao aluno dono do plano.
9. Não se excluem alunos ou planos que tenham registros dependentes.

## 6. Modelo de dados
Consulte `DER.md` para as entidades, atributos, chaves e cardinalidades. `schema.sql` é a fonte de verdade para a estrutura relacional.

## 7. Plano de testes
- **CT01 Login válido:** informar `admin` e `FitLife@123`; verificar abertura do painel.
- **CT02 Login inválido:** informar senha incorreta; verificar mensagem e permanência na tela de login.
- **CT03 Expiração:** ficar sem atividade por 20 minutos; a próxima requisição deve redirecionar ao login.
- **CT04 Cadastro de aluno:** cadastrar aluno com CPF de 11 dígitos; verificar gravação e que o banco não contém CPF em texto puro.
- **CT05 Busca:** pesquisar por nome parcial; verificar apenas registros correspondentes.
- **CT06 Edição de aluno:** alterar telefone ou cidade; verificar persistência após recarregar.
- **CT07 Plano sem aluno:** tentar cadastrar plano sem aluno; o formulário deve impedir a operação.
- **CT08 Plano válido:** selecionar aluno existente e salvar; verificar FK correta.
- **CT09 Agendamento:** criar agendamento com aluno e plano correspondentes.
- **CT10 Plano de outro aluno:** tentar combinar aluno A com plano de aluno B; a aplicação deve rejeitar.
- **CT11 Ordenação:** cadastrar agendamentos em datas diferentes; verificar ordem crescente.
- **CT12 Edição de data:** alterar data/hora; verificar atualização no banco e na listagem.
- **CT13 Integridade referencial:** tentar excluir aluno/plano vinculado; verificar mensagem amigável.
- **CT14 Dados iniciais:** executar `inserts.py` e conferir pelo menos três registros em cada tabela.

## 8. Privacidade e LGPD
O sistema reduz a exposição do CPF usando criptografia, mas isso sozinho não garante conformidade integral com a LGPD. Em uso real, a academia deve definir finalidade e base legal, limitar acessos, informar os titulares, proteger backups, estabelecer retenção e descarte, registrar incidentes e manter a chave de criptografia segura. Os dados incluídos no script são demonstrativos.

## 9. Como executar
Siga o passo a passo do `README.md`: criar banco com `schema.sql`, configurar conexão, instalar `requirements.txt`, executar `inserts.py` e iniciar `app.py`.
