import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts')) # solução temporária já que chamar direto via .scripts causa erro de importação

from config_database import engine, Base, SessionLocal
from models import Book, User
from insert_database import save_to_database
from scrapping import scrape_books
from utils import CategoryEnum
from fastapi import FastAPI, Depends, HTTPException, status, Query


app = FastAPI(
    title = "API de consulta aos dados do site Books to Scrape",
    description = "API desenvolvida para consultar os dados extraídos do site Books to Scrape para o tech challenge da Fase 1 da Pós-tech Machine Learning Engineering da FIAP.",
    version= "1.0.0"
)

# Dependência para abrir/fechar sessão no banco de dados
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
# Endpoint de teste para validar o banco de dados criado
@app.post("/test-book")
def create_test_book(db: Base = Depends(get_database)):
    """
    ### Descrição:
    Rota de teste para validar criação dos registros no banco de dados

    ### Retorno:
    Cria um livro de teste no banco e retorna os dados do livro criado.
    
    ### Body JSON:
        {
            "title": "Livro Teste",
            "category": "Ficção",
            "availability": "In Stock",
            "rating": 4,
            "id": 1,
            "price": 20.5,
            image_url=None
        }'
    
    """  
    # Criar livro de teste
    book = Book(
        title="Livro Teste",
        price=20.5,
        category="Ficção",
        rating=4,
        availability="In Stock",
        image_url=None
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    
    return {
        "id": book.id,
        "title": book.title,
        "price": book.price,
        "category": book.category,
        "rating": book.rating,
        "availability": book.availability,
        "image_url": book.image_url
    }

# rota de inserir livros extraídos do site no banco de dados
@app.post("/insert-books", 
          status_code=200,
          responses={
            200: {
                "description": "Livros processados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "3 livros processados.",
                            "failures": "1 livro que apresentou falhas."
                        }
                    }
                }
            },
            400:    {
                "description": "Erro na validação dos tipos dos dados. Verifique a integridade dos dados enviados.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                {
                                    "loc": ["body", 0, "price"],
                                    "msg": "value is not a valid float",
                                    "type": "type_error.float"
                                }
                            ]
                        }
                    }
                }
            }
        }
    )
async def insert_books(list_books: list[dict]):
    """
    ### Descrição:
    Rota para inserir livros extraídos via scrapping no banco de dados.
    ### Parâmetros:
    - body: lista de livros
        - title: str
        - price: float
        - category: str
        - rating: int
        - availability: str
        - image_url: str (opcional)

    ### Retorno:
    - message: quantidade de livros processados
    - failures: quantidade de livros que apresentaram falhas e foram registrados

    ### Body JSON:
        {
            "id": 1,
            "title": "It's Only the Himalayas",
            "price": 45.17,
            "category": "Travel",
            "rating": 2,
            "availability": "In stock",
            "image_url": "https://books.toscrape.com/media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg"
        }
    """

    result = save_to_database(list_books)
    return {
        "message": f"{len(result['saved'])} livros processados.",
        "failures": f"{len(result['failures'])} livros que apresentaram falhas."
    }

# Rota para buscar livros por título e/ou categoria
@app.get("/api/v1/books/search", 
         status_code=200,
         responses={
            200: {
                "description": "Livros encontrados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                                "total livros encontrados": 1,
                                "livros": [
                                    {
                                    "title": "Under the Tuscan Sun",
                                    "category": "Travel",
                                    "availability": "In stock",
                                    "rating": 3,
                                    "id": 5,
                                    "price": 37.33,
                                    "image_url": "https://books.toscrape.com/media/cache/98/c2/98c2e95c5fd1a4e7cd5f2b63c52826cb.jpg"
                                    }
                                ]
                            }
                    }
                }
            },
            404:    {
                "description": "Nenhum livro encontrado com os parâmetros informados. Revise os dados e tente novamente.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Nenhum livro encontrado com os parâmetros informados. Revise os dados e tente novamente."
                        }
                    }
                }
            },
            400:    {
                "description": "Informe pelo menos o título ou a categoria para realizar a busca.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Informe pelo menos o título ou a categoria para realizar a busca."

                        }
                    }
                }
            }
        }
)
async def search_books_items(
        title: str = Query(None, description="Título do livro - Ex: Under the Tuscan Sun"), # testando parametros personalizados na documentação
        #category: str = Query(None, description="Categoria do livro - Ex: Fiction"), # testando parametros personalizados na documentação
        category: CategoryEnum = Query(None, description="Categoria do livro - Ex: Fiction", ), # para adicionar o dropdown com as categorias
        db: Base = Depends(get_database)):
    """
        ### Descrição:
        Rota para buscar livros por título e/ou categoria.
        ### Parâmetros:
        - title: str (opcional, pesquisa parcial, insensível a maiúsculas)
        - category: str (opcional, pesquisa parcial, insensível a maiúsculas

        ### Retorno:
        Listagem de livros que atendem aos critérios de busca por título e/ou categoria. 
        - Caso não sejam informados algum dos parâmetros, retorna erro 400.
        - Request URL: 'http://127.0.0.1:8000/api/v1/books/search?title={title}&category={category}'
    """  
    
    
    if not title and not category:
        raise HTTPException(status_code=400, detail="Informe pelo menos o título ou a categoria para realizar a busca.")
    
    #vai montar a query dinamicamente conforme os parâmetros informados
    query = db.query(Book)
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if category:
        query = query.filter(Book.category == category.value)

    books = query.all()

    if len(books) > 0:
        return {
                 "total livros encontrados": len(books),
                 "livros": books
            }
    raise HTTPException(status_code=404, detail="Nenhum livro encontrado com os parâmetros informados. Revise os dados e tente novamente.")


# Rota para buscar livros por valores min e max de preço
@app.get("/api/v1/books/price-range", 
         status_code=200,
         responses={
            200: {
                "description": "Livros encontrados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                                        "total livros encontrados": 3,
                                        "livros": [
                                            {
                                            "title": "The Tipping Point: How Little Things Can Make a Big Difference",
                                            "category": "Add a comment",
                                            "availability": "In stock",
                                            "id": 667,
                                            "price": 10.02,
                                            "rating": 2,
                                            "image_url": "https://books.toscrape.com/media/cache/27/3d/273d4c813111bc482e8c473ebd90fbbb.jpg"
                                            },
                                            {
                                            "title": "An Abundance of Katherines",
                                            "category": "Young Adult",
                                            "availability": "In stock",
                                            "id": 782,
                                            "price": 10,
                                            "rating": 5,
                                            "image_url": "https://books.toscrape.com/media/cache/ed/45/ed4517339d4780f4158c485c83850d20.jpg"
                                            },
                                            {
                                            "title": "The Origin of Species",
                                            "category": "Science",
                                            "availability": "In stock",
                                            "id": 805,
                                            "price": 10.01,
                                            "rating": 4,
                                            "image_url": "https://books.toscrape.com/media/cache/da/0d/da0d13699a090516502257a4d7da623f.jpg"
                                            }
                                        ]
                                    }
                    }
                }
            },
            404:    {
                "description": "Nenhum livro encontrado com os preços informados. Revise os dados e tente novamente..",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Nenhum livro encontrado com os preços informados. Revise os dados e tente novamente.."
                        }
                    }
                }
            },
            400:    {
                "description": "Informe o valor desejado para realizar a busca..",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Informe o valor desejado para realizar a busca."

                        }
                    }
                }
            }
        }
)
async def search_books_price_range(
        min_price: float = Query(description="Preço mínimo do livro", ge=0.01), # testando parametros personalizados na documentação
        max_price: float = Query(description="Preço máximo do livro", le=99.99), # testando parametros personalizados na documentação
        db: Base = Depends(get_database)):
    """
        ### Descrição:
        Rota para  buscar livros por valores mínimos e máximos.
        ### Parâmetros:
        - min_price: float (opcional, onde o valor mínimo é 0.0)
        - max_price : float (opcional, onde o valor máximo é 99.99)

        ### Retorno:
        Listagem de livros que atendem aos critérios de busca pelo range de preço.
        - Caso não sejam informados algum dos parâmetros, retorna erro 400.
        - Caso não seja encontrado algum livro dentro do parâmetro, retorna erro 404.
        - Request URL: 'http://127.0.0.1:8000/api/v1/books/search?min_price={min_price}&max_price={max_price}'
    """  
    
    
    if not min_price and not max_price:
        raise HTTPException(status_code=400, detail= "Informe o valor desejado para realizar a busca.")
    
    filtered_books = db.query(Book).filter(Book.price >= min_price, Book.price <= max_price).all()

    if len(filtered_books) > 0:
        return {
                 "total livros encontrados": len(filtered_books),
                 "livros": filtered_books
            }
    raise HTTPException(status_code=404, detail="Nenhum livro encontrado com os preços informados. Revise os dados e tente novamente.")


# Rota para buscar livros por valores min e max de preço
@app.get("/api/v1/books/top-rated", 
         status_code=200,
         responses={
            200: {
                "description": "Livros encontrados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                                    "total livros encontrados": 196,
                                    "livros": [
                                        {
                                            "title": "1,000 Places to See Before You Die",
                                            "category": "Travel",
                                            "availability": "In stock",
                                            "id": 11,
                                            "price": 26.08,
                                            "rating": 5,
                                            "image_url": "https://books.toscrape.com/media/cache/d7/0f/d70f7edd92705c45a82118c3ff6c299d.jpg"
                                            },
                                            {
                                            "title": "A Time of Torment (Charlie Parker #14)",
                                            "category": "Mystery",
                                            "availability": "In stock",
                                            "id": 20,
                                            "price": 48.35,
                                            "rating": 5,
                                            "image_url": "https://books.toscrape.com/media/cache/e8/c0/e8c0ba15066bab950ae161fd60949b9a.jpg"
                                            },
                                            {
                                            "title": "What Happened on Beale Street (Secrets of the South Mysteries #2)",
                                            "category": "Mystery",
                                            "availability": "In stock",
                                            "id": 29,
                                            "price": 25.37,
                                            "rating": 5,
                                            "image_url": "https://books.toscrape.com/media/cache/c7/ab/c7abb5e32bd37118a87523dcee0a70a6.jpg"
                                        }
                                    ]
                                }
                    }
                }
            },
            404:    {
                "description": "Nenhum livro encontrado com a avaliação informada. Revise os dados e tente novamente.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Nenhum livro encontrado com a avaliação informada. Revise os dados e tente novamente."
                        }
                    }
                }
            }
        }
)
async def search_books_rated(db: Base = Depends(get_database)):
    """
        ### Descrição:
        Rota para  buscar livros com maior nota de avaliação (5)

        ### Retorno:
        Listagem de livros que atendem aos critérios de busca.
        - Caso não seja encontrado algum livro dentro do parâmetro, retorna erro 404.
        - Request URL: 'http://127.0.0.1:8000/api/v1/books/top_rated'
    """  
    
    top_rating_books = db.query(Book).filter(Book.rating == 5).all()

    if len(top_rating_books) > 0:
        return {
                 "total livros encontrados": len(top_rating_books),
                 "livros": top_rating_books
            }
    raise HTTPException(status_code=404, detail="Nenhum livro encontrado com a avaliação informada. Revise os dados e tente novamente.")


#Rota para retornar todos os livros cadastrados no banco de dados
@app.get("/api/v1/books",
         status_code=200,
         responses={
            200: {
                "description": "Total de livros cadastrados:",
                "content": {
                    "application/json": {
                        "example": {
                            "total de livros": 1000,
                            "livros": [
                                {
                                    "title": "Livro Teste",
                                    "category": "Ficção",
                                    "availability": "In Stock",
                                    "rating": 4,
                                    "id": 1,
                                    "price": 20.5,
                                    "image_url": None
                                },
                                {
                                    "title": "Full Moon over Noahâs Ark: An Odyssey to Mount Ararat and Beyond",
                                    "category": "Travel",
                                    "availability": "In stock",
                                    "rating": 4,
                                    "id": 2,
                                    "price": 49.43,
                                    "image_url": "https://books.toscrape.com/media/cache/57/77/57770cac1628f4407636635f4b85e88c.jpg"
                                },
                                {
                                    "title": "See America: A Celebration of Our National Parks & Treasured Sites",
                                    "category": "Travel",
                                    "availability": "In stock",
                                    "rating": 3,
                                    "id": 3,
                                    "price": 48.87,
                                    "image_url": "https://books.toscrape.com/media/cache/9a/7e/9a7e63f12829df4b43b31d110bf3dc2e.jpg"
                                }
                            ]
                        }
                    }
                }
            },
            404: {
                "description": "Erro na validação dos tipos dos dados. Verifique a integridade dos dados enviados.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Nenhum livro encontrado. Faça a importação via scrapping e tente novamente."
                        }
                    }
                }
            }
        }
    )
async def get_books(db: Base = Depends(get_database)):
    """
    ### Descrição:
    Rota para listar todos os livros do banco de dados.

    ### Retorno:
    - total de livros: quantidade de livros processados
    - livros: listagem com detalhes de todos os livros cadastrados em formato json
    """
    books = db.query(Book).all()
    if len(books) > 0:
        return {
            "total de livros": len(books),
            "livros": books
            }
    raise HTTPException(status_code=404, detail="Nenhum livro cadastrado. Faça a importação via scrapping e tente novamente.")


# Rota para retorna detalhes completos de um livro específico pelo ID // ATUALIZAR OS RESPONSES
@app.get("/api/v1/books/{book_id}", 
         status_code=200)

async def get_book_by_id(book_id: int, db: Base = Depends(get_database)):
    """
    ### Descrição:
    Rota para pegar dados de um livro específico pelo ID de cadastro.
    ### Parâmetros:
    - BOOK_ID: int (obrigatório, vai de 1 a 1000 conforme cadastro no banco de dados)

    ### Retorno:
    Dados completos do livro, filtrado pelo seu ID.
    - Request URL: 'http://127.0.0.1:8000/api/v1/books/<book_id>'
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is not None:
        return book
    raise HTTPException(status_code=422, detail="Item não encontrado, verifique o ID informado")

# Rota para listar as categorias de livros disponíveis
@app.get("/api/v1/categories", 
         status_code=200,
         responses={
            200: {
                "description": "Total de livros cadastrados:",
                "content": {
                    "application/json": {
                        "example": {
                            "total de categorias": 51,
                            "categorias": [
                                "Ficção",
                                "Travel",
                                "Mystery",
                                "Historical Fiction",
                                "Sequential Art",
                                "Classics",
                                "...",
                                "Crime"
                            ]
                        }
                    }
                }
            },
            404: {
                "description": "Sem categorias cadastradas no momento. Faça a importação via scrapping e tente novamente..",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Sem categorias cadastradas no momento. Faça a importação via scrapping e tente novamente."
                        }
                    }
                }
            }
        }
    )
async def get_categories(db: Base = Depends(get_database)):
    """
    ### Descrição:
    Rota para para listar as categorias de livros disponíveis

    ### Retorno:
    - total de categorias: quantidade de categorias cadastradas
    - categorias: listagem com categorias distintas
    
    """ 
    categories = db.query(Book.category).distinct().all() # cria uma tupla (chave/valor) com as categorias
    unique_categories = [c[0] for c in categories] # puxa os valores únicos da tupla retornada pelo distinct() 
    if len(unique_categories) > 0:
        return {
            "total de categorias": len(unique_categories),
            "categorias": unique_categories
        }

    raise HTTPException(status_code=404, detail="Sem categorias cadastradas no momento. Faça a importação via scrapping e tente novamente.")



    
    
    
    
# uv run uvicorn app.main:app --reload