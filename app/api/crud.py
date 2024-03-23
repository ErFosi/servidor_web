from passlib.context import CryptContext
from . import databaseORM
from . import esquemas
from sqlalchemy.orm import Session
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_usuario_por_nombre_usuario(db: Session, usuario: str):
    return db.query(databaseORM.Usuario).filter(databaseORM.Usuario.usuario == usuario).first()
def get_usuario(db: Session, usuario_id: int):
    return db.query(databaseORM.Usuario).filter(databaseORM.Usuario.id == usuario_id).first()
# Usuarios
def crear_usuario(db: Session, usuario: esquemas.UsuarioCreate):
    # Verifica si el usuario ya existe
    usuario_existente = obtener_usuario_por_nombre_usuario(db, usuario=usuario.usuario)
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    # Si el usuario no existe, procede a crear uno nuevo
    hashed_password = hash_password(usuario.contraseña)  # Hashea la contraseña
    db_usuario = databaseORM.Usuario(usuario=usuario.usuario, contraseña=hashed_password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(databaseORM.Usuario).offset(skip).limit(limit).all()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(databaseORM.Usuario).filter(databaseORM.Usuario.usuario == username).first()
    if not user:
        return False
    if not verify_password(password, user.contraseña):
        return False
    return user

# Actividades
def crear_actividad(db: Session, actividad: esquemas.ActividadCreate, id_usuario: int):
    db_actividad = databaseORM.Actividad(**actividad.dict(),id_usuario=id_usuario)
    db.add(db_actividad)
    db.commit()
    db.refresh(db_actividad)
    return db_actividad

def obtener_actividades(db: Session, skip: int = 0, limit: int = 100):
    return db.query(databaseORM.Actividad).offset(skip).limit(limit).all()

def obtener_actividades_por_usuario(db: Session, usuario_id: int):
    return db.query(databaseORM.Actividad).filter(databaseORM.Actividad.id_usuario == usuario_id).all()

# Ubicaciones
def crear_ubicacion(db: Session, ubicacion: esquemas.UbicacionCreate, id_actividad: int):
    db_ubicacion = databaseORM.Ubicacion(**ubicacion.dict(), idActividad=id_actividad)
    db.add(db_ubicacion)
    db.commit()
    db.refresh(db_ubicacion)
    return db_ubicacion

def obtener_ubicaciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(databaseORM.Ubicacion).offset(skip).limit(limit).all()