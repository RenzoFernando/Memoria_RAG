"""Proveedores configurables. Auto prefiere Ollama y luego Gemini/Anthropic."""
import os, json
from pathlib import Path
from urllib.request import Request, urlopen
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

def _ollama(ruta, datos=None, timeout=3):
    url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + ruta
    req = Request(url, data=json.dumps(datos).encode() if datos is not None else None,
                  headers={"Content-Type":"application/json"})
    with urlopen(req, timeout=timeout) as r:
        return json.load(r)

def seleccionar_proveedor():
    elegido = os.getenv("LLM_PROVIDER", "auto").lower().strip()
    if elegido != "auto":
        if elegido not in {"ollama","gemini","anthropic","simulado"}:
            raise ValueError("LLM_PROVIDER debe ser auto, ollama, gemini o anthropic.")
        return elegido
    try:
        modelos = _ollama("/api/tags").get("models", [])
        nombre = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        if any(m.get("name") == nombre for m in modelos): return "ollama"
    except Exception:
        pass
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"): return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"): return "anthropic"
    raise RuntimeError("Configura Ollama con el modelo indicado o una clave Gemini/Anthropic en .env.")

def llamar_llm(sistema, mensajes, max_tokens=1024):
    if not mensajes: raise ValueError("La lista de mensajes no puede estar vacía.")
    proveedor = seleccionar_proveedor()
    if proveedor == "simulado": return "[respuesta simulada] " + str(mensajes[-1]["content"])[:200]
    try:
        if proveedor == "ollama":
            r = _ollama("/api/chat", {"model":os.getenv("OLLAMA_MODEL","qwen2.5:1.5b"),
                "messages":[{"role":"system","content":sistema}]+mensajes,"stream":False,
                "options":{"num_ctx":4096,"num_predict":max_tokens}},timeout=180)
            return r["message"]["content"]
        if proveedor == "gemini":
            from google import genai
            from google.genai import types
            clave = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not clave: raise ValueError("Falta GEMINI_API_KEY.")
            with genai.Client(api_key=clave) as cliente:
                r=cliente.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"),
                    contents=[types.Content(role="model" if m["role"]=="assistant" else "user",
                        parts=[types.Part.from_text(text=m["content"])]) for m in mensajes],
                    config=types.GenerateContentConfig(system_instruction=sistema,max_output_tokens=max_tokens))
            if not r.text: raise RuntimeError("Gemini devolvió una respuesta vacía.")
            return r.text
        import anthropic
        if not os.getenv("ANTHROPIC_API_KEY"): raise ValueError("Falta ANTHROPIC_API_KEY.")
        with anthropic.Anthropic() as cliente:
            r=cliente.messages.create(model=os.getenv("ANTHROPIC_MODEL","claude-sonnet-5-5"),
                system=sistema,messages=mensajes,max_tokens=max_tokens)
        return "".join(b.text for b in r.content if hasattr(b,"text"))
    except Exception as exc:
        # Never expose provider request URLs or API keys in console errors.
        raise RuntimeError(f"Falló {proveedor} ({type(exc).__name__}). Revisa conexión, modelo y clave en .env. Puedes cambiar LLM_PROVIDER.") from None
