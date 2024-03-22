from typing import Union
from fastapi import FastAPI
from sqlalchemy.orm import Session
from .database import SessionLocal
from fastapi import Depends
from typing import List
from .databaseORM import Usuario,Ubicacion,Actividad
from .esquemas import Usuario,Actividad,ActividadBase,ActividadCreate,Ubicacion,UbicacionBase,UbicacionCreate,UsuarioBase,UsuarioCreate
from . import crud

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
def crear_actividad(actividad: ActividadCreate, id_usuario: int, db: Session = Depends(get_db)):
    return crud.crear_actividad(db=db, actividad=actividad, id_usuario=id_usuario)

@app.get("/actividades/", response_model=List[Actividad])
def leer_actividades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.obtener_actividades(db, skip=skip, limit=limit)

@app.post("/ubicaciones/", response_model=Ubicacion)
def crear_ubicacion(ubicacion: UbicacionCreate, id_actividad: int, db: Session = Depends(get_db)):
    return crud.crear_ubicacion(db=db, ubicacion=ubicacion, id_actividad=id_actividad)

@app.get("/ubicaciones/", response_model=List[Ubicacion])
def leer_ubicaciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.obtener_ubicaciones(db, skip=skip, limit=limit)