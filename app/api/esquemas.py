from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class UbicacionBase(BaseModel):
    latitud: float
    longitud: float

class UbicacionCreate(UbicacionBase):
    pass

class Ubicacion(UbicacionBase):
    id: int
    idActividad: int

    class Config:
        orm_mode = True

class ActividadBase(BaseModel):
    nombre: str
    tiempo: int = 0
    categoria: str = "Otros"
    start_time_millis: int 
    is_playing: bool = False
    fecha: date

class ActividadCreate(ActividadBase):
    pass


class Actividad(ActividadBase):
    id: int
    id_usuario: int 
    ubicaciones: List[UbicacionBase] = []  

    class Config:
        orm_mode = True

class UsuarioBase(BaseModel):
    usuario: str

class UsuarioCreate(UsuarioBase):
    contraseña: str

class AuthForm(BaseModel):
    username: str
    password: str


class Usuario(UsuarioBase):
    id: int
    actividades: List[Actividad] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: str | None = None

class TokenConUsuario(BaseModel):
    access_token: str
    refresh_token: str  # Nuevo campo para el refresh token
    token_type: str