from typing import Union
from fastapi import FastAPI
from google.auth import jwt
from sqlalchemy.orm import Session
from .database import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from .databaseORM import Usuario,Ubicacion,Actividad
from .esquemas import *
from . import crud
from .oauth import obtener_usuario_actual, crear_token_acceso, SECRET_KEY
from datetime import datetime, timedelta

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/usuarios/", response_model=Usuario)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return crud.crear_usuario(db=db, usuario=usuario)

@app.get("/usuarios/", response_model=List[Usuario])
def leer_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.obtener_usuarios(db, skip=skip, limit=limit)

@app.post("/actividades/", response_model=Actividad)
def crear_actividad(
    actividad: ActividadCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return crud.crear_actividad(db=db, actividad=actividad, id_usuario=usuario_actual.id)

@app.get("/actividades/", response_model=List[Actividad])
def leer_actividades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.obtener_actividades(db, skip=skip, limit=limit)


@app.get("/mis_actividades/", response_model=List[Actividad])
def leer_mis_actividades(db: Session = Depends(get_db),usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    actividades = crud.obtener_actividades_por_usuario(db, usuario_id=usuario_actual.id)
    return actividades




@app.post("/ubicaciones/", response_model=Ubicacion)
def crear_ubicacion(
    ubicacion: UbicacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return crud.crear_ubicacion(db=db, ubicacion=ubicacion, id_actividad=usuario_actual.id)


@app.get("/ubicaciones/", response_model=List[Ubicacion])
def leer_ubicaciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.obtener_ubicaciones(db, skip=skip, limit=limit)


@app.post("/token", response_model=TokenConUsuario)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = crud.authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar el token de acceso
    access_token_expires = timedelta(minutes=30)  # O el tiempo que consideres adecuado
    access_token = crear_token_acceso(
        data={"sub": str(usuario.id)}
    )

    # Generar el refresh token
    refresh_token_expires = timedelta(days=7)  # Los refresh tokens suelen tener una mayor duración
    refresh_token = crear_token_acceso(  # Suponiendo que reutilizas la misma función con un parámetro adicional
        data={"sub": str(usuario.id),"refresh":True}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,  # Incluir el refresh token en la respuesta
        "usuario": usuario
    }


"""
@app.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    # Verificar la validez del refresh token aquí
    # Esto podría involucrar verificar la firma del token, su expiración y si ha sido revocado
    usuario_id = verificar_refresh_token(refresh_token)
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar un nuevo token de acceso
    access_token_expires = timedelta(minutes=30)
    access_token = crear_token_acceso(
        data={"sub": str(usuario_id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

def verificar_refresh_token(refresh_token: str, db: Session):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            return None
        # Aquí puedes añadir más verificaciones, como si el token ha sido revocado
    except JWTError:
        return None
    return usuario_id
    """