from typing import Union
import os
import logging
from fastapi import FastAPI
from google.auth import jwt
from sqlalchemy.orm import Session
from .database import SessionLocal
from fastapi import Depends, HTTPException, status,UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from .databaseORM import Usuario,Ubicacion,Actividad
from .esquemas import *
from . import crud
from fastapi.responses import FileResponse
from .oauth import obtener_usuario_actual, crear_token_acceso, SECRET_KEY
from datetime import datetime, timedelta
import glob


VALID_IMG_TYPES = ['image/jpeg', 'image/png', 'image/webp']
app = FastAPI()
image_folder = "/code/images"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/usuarios/", response_model=UsuarioResponse)
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


@app.get("/mis_actividades/",tags=["Sync"], response_model=List[Actividad])
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


@app.post("/token",tags=["Oauth"], response_model=TokenConUsuario)
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
        "refresh_token": refresh_token
    }


@app.post("/sincronizar_actividades/",tags=["Sync"], status_code=status.HTTP_200_OK)
def sincronizar_actividades(actividades_data: ActividadesList, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    # Eliminar todas las actividades y ubicaciones existentes para este usuario
    crud.eliminar_actividades_por_usuario(db, usuario_id=usuario_actual.id)
    
    # Insertar las nuevas actividades y ubicaciones proporcionadas
    for actividad_data in actividades_data.actividades:
        crud.crear_actividad_con_ubicaciones(db, actividad_data=actividad_data, usuario_id=usuario_actual.id)
    
    return {"mensaje": "Actividades sincronizadas con éxito"}

@app.get("/profile/image", tags=["Profile"], status_code=status.HTTP_200_OK, response_class=FileResponse)
async def get_user_profile_image(usuario_actual: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    # Define la carpeta donde se almacenarán las imágenes
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    VALID_IMG_EXT = ['.jpeg', '.png', '.webp', '.jpg']
    enc=False
    # Intenta encontrar una imagen que coincida con las extensiones válidas
    for extension in VALID_IMG_EXT:
        image_path = os.path.join(image_folder, f"{usuario_actual.id}{extension}")
        if os.path.isfile(image_path):
            enc=True
            return FileResponse(image_path)
        
    if (not enc):
        # Si no se encuentra ninguna imagen válida, devuelve la imagen predeterminada
        default_image_path = os.path.join(image_folder, "default.jpg")
        if not os.path.isfile(default_image_path):
            raise HTTPException(status_code=404, detail="Default image not found.")
        return FileResponse(default_image_path)


@app.post("/profile/image", tags=["Profile"], status_code=status.HTTP_201_CREATED)
async def upload_user_profile_image(file: UploadFile, usuario_actual: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    # Asegúrate de que el archivo sea de un tipo válido
    if file.content_type not in ['image/jpeg', 'image/png', 'image/webp']:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Construye el patrón del nombre del archivo con el ID del usuario y cualquier extensión de archivo de imagen válida
    pattern = f"{usuario_actual.id}.*"
    search_path = os.path.join(image_folder, pattern)

    # Busca cualquier archivo existente que coincida con el patrón
    existing_files = glob.glob(search_path)
    for file_path in existing_files:
        try:
            os.remove(file_path)
        except Exception as e:
            # Maneja el caso en que el archivo no pueda ser eliminado
            raise HTTPException(status_code=500, detail="Could not remove existing file")

    # Procede con la lógica para guardar el nuevo archivo
    extension = os.path.splitext(file.filename)[1]  # Obtiene la extensión del archivo subido
    file_name = f"{usuario_actual.id}{extension}"
    file_path = os.path.join(image_folder, file_name)

    contents = await file.read()
    # Guarda el archivo subido en el sistema de archivos
    with open(file_path, 'wb') as f:
        f.write(contents)

    # Aquí puedes añadir lógica adicional, como actualizar la base de datos con el path del archivo

    return {"filename": file_name}
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