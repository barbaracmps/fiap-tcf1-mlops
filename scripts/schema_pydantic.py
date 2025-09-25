from pydantic import BaseModel, EmailStr
from datetime import datetime
# vai validar o schema a partir dos dados exportados via scrapping (validar depois com arquivo final) 
# Add os campos que serão exportados
class Books(BaseModel):
    id: int
    title: str
    price: float
    category: str
    rating: int = None
    availability: str = None
    image_url: str = None
    
    class Config:
        orm_mode = True # orm_mode = True permite converter objetos SQLAlchemy direto para Pydantic.

# valida a criação do usuário no banco e depois vai hashear a senha para melhorar a segurança
class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str # depois será hasheado

# retorna apenas dados para leitura dos dados do usuário
class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    
    class Config:
        orm_mode = True
   
# será usada para verificar a senha/tokens
class LoginUser(BaseModel):
    username: str
    password: str

# será usada para guardar os erros
class FailedBookLog(BaseModel):
    title: str
    error: str
    created_at: datetime = None