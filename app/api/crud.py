from passlib.context import CryptContext
from . import databaseORM
from . import esquemas
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

# Usuarios
def crear_usuario(db: Session, usuario: esquemas.UsuarioCreate):
    hashed_password = hash_password(usuario.contraseña)  # Hashea la contraseña
    db_usuario = databaseORM.Usuario(usuario=usuario.usuario, contraseña=hashed_password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(databaseORM.Usuario).offset(skip).limit(limit).all()


# Actividades
def crear_actividad(db: Session, actividad: esquemas.ActividadCreate, id_usuario: int):
    db_actividad = databaseORM.Actividad(**actividad.dict(), idUsuario=id_usuario)
    db.add(db_actividad)
    db.commit()
    db.refresh(db_actividad)
    return db_actividad

def obtener_actividades(db: Session, skip: int = 0, limit: int = 100):
    return db.query(databaseORM.Actividad).offset(skip).limit(limit).all()

# Ubicaciones
def crear_ubicacion(db: Session, ubicacion: esquemas.UbicacionCreate, id_actividad: int):
    db_ubicacion = databaseORM.Ubicacion(**ubicacion.dict(), idActividad=id_actividad)
    db.add(db_ubicacion)
    db.commit()
    db.refresh(db_ubicacion)
    return db_ubicacion

def obtener_ubicaciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(databaseORM.Ubicacion).offset(skip).limit(limit).all()