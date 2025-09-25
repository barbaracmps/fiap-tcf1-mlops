# Projeto Tech Challange 7MLE - Fase 1 - Scrapping e API em Fast API
## O que é este projeto

Esta API foi desenvolvida para consultar os dados extraídos do site Books to Scrape (https://books.toscrape.com) para o tech challenge da Fase 1 da Pós-tech Machine Learning Engineering da FIAP.

---

## Stacks utilizadas

- **Linguagem:** Python 3.10
- **Framework Web:**  FastAPI
- **Servidor ASGI:** Uvicorn
- **Gerenciador de dependências:**  uv
- **Scraping:**  BeautifulSoup, requests
- **Banco de dados:**  SQLAlchemy (via sqlite3)
- **Validação:**  Pydantic
- **Autenticação:**  [EM BREVE]
---
## Link do Deploy no Render

[EM BREVE]

## APIs
http://127.0.0.1:8000/docs#/ [EM BREVE ESTARÁ EM DEPLOY]

## Arquitetura do Projeto

- `app/main.py` → arquivo principal da API
- `models.py` → definição das entidades do banco (Book, User)
- `config_database.py` → configuração do SQLAlchemy e SQLite
- `insert_database.py` → funções para injetar dados extraídos via scraping nas tabelas do banco de dados
- `scrapping.py` → funções para scraping dos livros a partir do site Books to Scrape
- `utils.py` → Scripts com funções utilitárias

## Como rodar localmente

#### 1. Clone o repositório
No terminal, execute os comandos:
```bash
git clone https://github.com/barbaracmps/fiap-tcf1-mlops.git
cd fiap-tcf1-mlops
```

#### 2. Instale e inicialize o uv
No terminal, execute os comandos:
```bash
    pip install uv
```
E depois inicialize o pacote no terminal:
```bash
    uv init
```
Esse comando vai faz:
- Ativa o ambiente virtual já configurado
- Instala todas as dependências listadas
- Configura a estrutura inicial do projeto

#### 3. Execute a aplicação localmente
Acesse o arquivo main.py e rode no terminal o uvicorn
```bash
uv run uvicorn app.main:app --reload
```

#### 4. Acesse a aplicação
API: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs
Redoc: http://127.0.0.1:8000/redoc

#### 5. Documentação das principais rotas criadas até então

## Rotas da API

| Rota | Método | Objetivo | Parâmetros | Notas |
|------|--------|----------|------------|-------|
| `/test-book` | POST | Criar um livro de teste no banco de dados para validação do setup. | Nenhum | Cria automaticamente um livro fixo para testes. |
| `/insert-books` | POST | Inserir livros enviados via JSON no banco de dados. | Body: lista de livros (title, price, category, rating, availability, image_url) | Valida os dados; retorna quantidade de livros processados e falhas. |
| `/api/v1/books/search` | GET | Pesquisar livros por título parcial e/ou categoria. | Query: `title` (opcional), `category` (opcional) | Pelo menos um parâmetro deve ser informado. |
| `/api/v1/books/price-range` | GET | Listar livros dentro de um intervalo de preço. | Query: `min_price` (opcional), `max_price` (opcional) | Retorna erro 400 se nenhum parâmetro for informado. |
| `/api/v1/books/top-rated` | GET | Retornar livros com avaliação máxima (rating = 5). | Nenhum | Filtra apenas livros com nota máxima. |
| `/api/v1/books` | GET | Retornar todos os livros cadastrados no banco de dados. | Nenhum | Lista completa do banco de dados. |
| `/api/v1/books/{book_id}` | GET | Retornar dados completos de um livro específico pelo ID. | Path: `book_id` (obrigatório) | Retorna erro 422 se o ID não existir. |
| `/api/v1/categories` | GET | Retornar todas as categorias distintas dos livros cadastrados. | Nenhum | Lista apenas categorias únicas. |