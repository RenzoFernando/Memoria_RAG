"""Conexión con el modelo de lenguaje (LLM)."""
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MODELO = "claude-sonnet-5-5"  # Cambie el modelo según su proveedor

def llamar_llm(sistema: str, mensajes: list[dict[str, Any]], max_tokens: int = 1024) -> str:
   """Envía un prompt de sistema y una lista de mensajes al LLM y devuelve el texto."""
   if not mensajes:
       raise ValueError("La lista de mensajes no puede estar vacía.")

   if os.environ.get("ANTHROPIC_API_KEY"):
       import anthropic

       cliente = anthropic.Anthropic()
       respuesta = cliente.messages.create(
           model=MODELO,
           max_tokens=max_tokens,
           system=sistema,
           messages=mensajes,
       )

       textos = []
       for bloque in getattr(respuesta, "content", []):
           if hasattr(bloque, "text"):
               textos.append(bloque.text)
       if textos:
           return "".join(textos)
       return ""

   # Modo de prueba: sin clave de API devuelve una respuesta simulada
   ultimo_mensaje = mensajes[-1]
   contenido = ultimo_mensaje.get("content", "")

   if isinstance(contenido, list):
       piezas = []
       for item in contenido:
           if isinstance(item, dict):
               pieza = item.get("text", str(item))
               piezas.append(str(pieza))
           else:
               piezas.append(str(item))
       contenido = " ".join(piezas)

   return "[respuesta simulada] " + str(contenido)[:200]

