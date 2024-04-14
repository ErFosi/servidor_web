from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import crud
from sqlalchemy.orm import Session
from .database import SessionLocal
import os

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



SECRET_KEY = os.getenv("SECRET_KEY", "un_valor_por_defecto_secreto")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def crear_token_acceso(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verificar_token_acceso(token: str, credenciales_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credenciales_exception
        expiration = payload.get("exp")
        if expiration is not None:
            expiration_date = datetime.fromtimestamp(expiration)
            if datetime.utcnow() > expiration_date:
                raise credenciales_exception
        return {"id": id}
    except JWTError:
        raise credenciales_exception

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(verificar_token_acceso(token, credenciales_exception))
    usuario_id: str = verificar_token_acceso(token, credenciales_exception)["id"]
    print(usuario_id)
    usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if usuario is None:
        raise credenciales_exception
    return usuario