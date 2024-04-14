
import firebase_admin
from firebase_admin import credentials, messaging
import google.auth
from google.auth.transport.requests import Request
from os import environ
from google.oauth2 import service_account
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import random
import os

print("-----------AUTO NOTIFICADOR ON--------------")

# Lista de mensajes de notificaciones
mensajes_notificaciones = [
    "El tiempo debe ser repartido en todo tipo de actividades, deporte formacion e incluso ocio.",
    "Gastar demasiado tiempo en ocio es peligroso!",
    "Apuntar el tiempo de cada tarea te puede ayudar a gestionar mejor tu dia a dia",
    "El algoritmo de Shor es muy complejo!",
    "Recuerda apuntar el tiempo invertido de tus tareas!",
    "Ten un buen día y distribuye bien el tiempo!"
]

# Configurar el planificador
scheduler = AsyncIOScheduler()
scheduler.start()

def enviar_mensaje_aleatorio():
    mensaje_aleatorio = random.choice(mensajes_notificaciones)
    message = messaging.Message(
        notification=messaging.Notification(
            title="Recordatorio Importante",
            body=mensaje_aleatorio,
        ),
        topic="actividades"
    )
    try:
        response = messaging.send(message)
        print(f"Mensaje enviado: {response}")
    except Exception as e:
        print(f"Error enviando mensaje: {str(e)}")

# Programar la tarea
scheduler.add_job(
    enviar_mensaje_aleatorio,
    trigger=CronTrigger(hour=21, minute=37),  # Ejecutar todos los días a las 10:00 AM
    timezone="Europe/Madrid"  # Asegúrate de poner tu zona horaria
)