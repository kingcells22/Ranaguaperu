import os
import json
from google import genai
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

# Cliente de Google GenAI
client = genai.Client(api_key=os.getenv("CHATBOT_API_KEY"))

# Cargar base de conocimientos
def cargar_kb():
    try:
        with open("data/knowledge.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando JSON: {e}")
        return {}

kb = cargar_kb()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request): return templates.TemplateResponse("index.html", {"request": request})

@app.get("/nosotros.html")
async def nosotros(request: Request): return templates.TemplateResponse("nosotros.html", {"request": request})

@app.get("/galeria.html")
async def galeria(request: Request): return templates.TemplateResponse("galeria.html", {"request": request})

@app.get("/catalogo.html")
async def catalogo(request: Request): return templates.TemplateResponse("catalogo.html", {"request": request})

# --- BUSCADOR MANUAL (PLAN B SEGURO) ---
def buscar_en_json(msg):
    msg = msg.lower()
    productos = kb.get('productos_destacados', [])
    numero_wa = kb.get('contacto', {}).get('whatsapp', '+51930174156').replace(" ", "").replace("+", "")
    
    # 1. Detectar intención de cotización o compra
    palabras_compra = ["cotizacion", "cotización", "cotizar", "precio", "comprar", "si deseo", "si quiero", "informacion general"]
    if any(p in msg for p in palabras_compra):
        # Enlace HTML directo a WhatsApp
        link_wa = f"<a href='https://wa.me/{numero_wa}?text=Hola,%20deseo%20una%20cotización' target='_blank' class='text-green-700 font-bold underline hover:text-green-800'>Haciendo clic aquí</a>"
        return f"¡Excelente! Para enviarte una cotización formal y detallada, por favor escríbenos a nuestro WhatsApp {link_wa}. ¡Te atenderemos de inmediato!"

    # 2. Mapeo de productos específicos
    mapeo = {
        "cinta": "Cinta de Goteo",
        "goteo": "Cinta de Goteo",
        "aspersor": "Aspersores de Impacto",
        "valvula": "Electroválvulas",
        "automatizacion": "Sistemas de Fertirriego"
    }

    for clave, nombre_real in mapeo.items():
        if clave in msg:
            for p in productos:
                if nombre_real.lower() in p.get('nombre', '').lower():
                    desc = p.get('descripcion') or p.get('beneficio') or "Excelente calidad."
                    return f"Sobre {p['nombre']}: {desc} El precio es {p.get('precio', 'a consultar')}. ¿Te gustaría una cotización?"
    return None

@app.post("/ask")
async def ask_bot(message: str = Form(...)):
    instrucciones = f"Eres el experto de Ranagua. Empresa: {kb.get('empresa')}. Responde muy corto (2 líneas)."

    try:
        # Intentamos con la IA
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"{instrucciones}\n\nCliente: {message}"
        )
        return JSONResponse(content={"reply": response.text})

    except Exception as e:
        print(f"DEBUG: La IA falló, entrando Plan B manual. Error: {e}")
        
        # Si la IA falla, usamos la lógica manual mejorada
        respuesta_manual = buscar_en_json(message)
        
        if respuesta_manual:
            return JSONResponse(content={"reply": respuesta_manual})
        
        return JSONResponse(content={"reply": "¡Hola! En Ranagua somos expertos en riego con tecnología Dayu. ¿Buscas información técnica sobre cintas, aspersores o automatización?"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.getenv("PORT", 8000)), reload=True)