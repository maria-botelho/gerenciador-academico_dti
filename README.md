# Sistema de Gestão e Análise de Desempenho Acadêmico 

`Maria Eduarda Botelho`

## Como Iniciar o Projeto (Setup)

Para rodar este projeto localmente, siga os passos abaixo:

<ol>
  <li> Certifique-se de ter as dependências instaladas:
  
        pip install Flask Flask-SQLAlchemy
  </li>
  
  <li>Acesse o arquivo app.py e, se necessário, descomente db.drop_all() para começar com um banco de dados limpo.</li>
  
  <li>Execute a aplicação:
  
        python app.py
  </li>
</ol>

## Visão Geral

O Sistema de Gestão e Análise de Desempenho Acadêmico (SGADA) é uma aplicação web leve e completa, desenvolvida para gerenciar o ciclo de vida dos dados educacionais. Ele oferece uma interface para o gerenciamento de registros e ferramentas de análise crítica para identificação imediata de alunos em destaque e em risco.

## Stack Tecnológico

* Backend: Python 3 (Framework Flask)

* ORM (Mapeamento Objeto-Relacional): Flask-SQLAlchemy

* Banco de Dados: SQLite (arquivo local banco.db)

* Frontend (Template): HTML/Jinja2 (incompleto)

## Funcionalidades Detalhadas

O sistema é dividido em três módulos principais:
<ol>
  <li> Gestão de Cadastro (CRUD)
  Permite o gerenciamento completo de todas as entidades do sistema:
  Alunos: Cadastro, visualização, atualização e exclusão de nome e taxa de frequência.
  Disciplinas: Cadastro, visualização, atualização e exclusão dos nomes das matérias.
  Notas: Inserção, atualização e exclusão das notas de cada aluno em cada disciplina.
  </li>

  <li> Análise de Performance (Relatório de Destaque)
  O sistema automatiza o cálculo das médias de notas por disciplina e gera um relatório rigoroso:
  Cálculo da Média: Determinação da nota média geral para cada disciplina com base nas notas registradas.
  Critério de Destaque: Listagem de todos os alunos que superaram a média da turma em todas as disciplinas em que possuem notas cadastradas. Este relatório identifica o grupo de melhor desempenho consistente.
  </li>

<li> Monitoramento de Risco (Assiduidade)
  Focado na prevenção de reprovação por falta, este módulo monitora a taxa de frequência de cada aluno:
  Alerta de Risco: Geração de um relatório exclusivo listando todos os alunos cuja taxa de frequência é inferior a 75%, sinalizando a necessidade urgente de intervenção.
</li>


</ol>



O sistema estará acessível em http://127.0.0.1:5153/.

