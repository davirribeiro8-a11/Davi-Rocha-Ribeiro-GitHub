# Diagrama Entidade-Relacionamento (DER) — FitLife

## Entidades e atributos

- **USUARIOS** (`id_usuario` PK, `nome`, `usuario` UNIQUE, `senha`, `criado_em`)
- **ALUNOS** (`id_aluno` PK, `nome`, `cpf_criptografado`, `idade`, `telefone`, `cidade`, `criado_em`)
- **PROFESSORES** (`id_professor` PK, `nome`, `telefone`, `especialidade`)
- **PLANOS_TREINAMENTO** (`id_plano` PK, `id_aluno` FK, `nome_plano`, `descricao`, `modalidade`, `valor_mensal`, `data_inicio`)
- **AGENDAMENTOS** (`id_agendamento` PK, `id_aluno` FK, `id_plano` FK, `id_professor` FK opcional, `data_agendamento`, `observacao`, `criado_em`)

## Relacionamentos e cardinalidades

- ALUNOS **1:N** PLANOS_TREINAMENTO: um aluno pode ter vários planos; cada plano pertence a um aluno.
- ALUNOS **1:N** AGENDAMENTOS: um aluno pode ter vários agendamentos; cada agendamento pertence a um aluno.
- PLANOS_TREINAMENTO **1:N** AGENDAMENTOS: um plano pode estar associado a vários agendamentos.
- PROFESSORES **1:N opcional** AGENDAMENTOS: um professor pode orientar vários agendamentos; um agendamento pode não ter professor definido.
- USUARIOS é usada para autenticação e não possui relacionamento obrigatório com as demais tabelas.

## Diagrama textual

```mermaid
erDiagram
    USUARIOS {
        int id_usuario PK
        varchar nome
        varchar usuario UK
        varchar senha
    }
    ALUNOS {
        int id_aluno PK
        varchar nome
        varchar cpf_criptografado
        int idade
        varchar telefone
        varchar cidade
    }
    PROFESSORES {
        int id_professor PK
        varchar nome
        varchar telefone
        varchar especialidade
    }
    PLANOS_TREINAMENTO {
        int id_plano PK
        int id_aluno FK
        varchar nome_plano
        text descricao
        varchar modalidade
        decimal valor_mensal
        date data_inicio
    }
    AGENDAMENTOS {
        int id_agendamento PK
        int id_aluno FK
        int id_plano FK
        int id_professor FK
        datetime data_agendamento
        varchar observacao
    }
    ALUNOS ||--o{ PLANOS_TREINAMENTO : possui
    ALUNOS ||--o{ AGENDAMENTOS : agenda
    PLANOS_TREINAMENTO ||--o{ AGENDAMENTOS : organiza
    PROFESSORES o|--o{ AGENDAMENTOS : orienta
```
