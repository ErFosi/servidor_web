from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float, BigInteger
from sqlalchemy.orm import relationship
from .database import Base
import datetime
from datetime import date

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, unique=True, index=True)
    contraseña = Column(String)

    actividades = relationship("Actividad", back_populates="propietario")

class Actividad(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    tiempo = Column(Integer, default=0)
    categoria = Column(String, default="Otros")
    start_time_millis = Column(BigInteger)
    is_playing = Column(Boolean, default=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    fecha = Column(Date, default=date.today())

    propietario = relationship("Usuario", back_populates="actividades")
    ubicaciones = relationship("Ubicacion", back_populates="actividad")

class Ubicacion(Base):
    __tablename__ = "ubicaciones"

    id = Column(Integer, primary_key=True, index=True)
    latitud = Column(Float)
    longitud = Column(Float)
    id_actividad = Column(Integer, ForeignKey("actividades.id"))

    actividad = relationship("Actividad", back_populates="ubicaciones")