from flask import Flask, render_template, request, jsonify
from chatbot.data import training_data
from chatbot.model import build_and_train_model, load_model, predict_cluster
import random 
import requests # 👈 Import necesario para la conexión a Ollama
import json 
import os 

app = Flask(__name__)

# --- Configuración de Ollama ---
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
# Puedes cambiar el modelo aquí. Asegúrate de que esté descargado (ej: ollama pull llama3)
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:1b") 

# 🚨 NUEVA CONFIGURACIÓN: Palabra clave para forzar la llamada a Ollama
LLAMA_TRIGGER_PHRASE = "hablar con llama" 

# Intentamos cargar el modelo (o entrenamos si no existe)
try:
    model, vectorizer = load_model()
    if model is None:
        model, vectorizer = build_and_train_model(training_data, n_clusters=6) # ✅ Número de grupos ajustable
except Exception as e:
    # Manejo de error si el modelo de clustering no se puede cargar/entrenar
    print(f"ADVERTENCIA: Falló la carga/entrenamiento del modelo de clustering: {e}")
    model, vectorizer = None, None

# Respuesta por grupo
RESPUESTAS = {
    0:["¡Hola! 😊 ¿Como estás?", 
        "¡Que gusto saludarte!",
        "¡Hola! ¿en que puedo ayudarte?" 
        ],
    1:["Hasta luego puto",
        "Nos vemos pronto",
        "Cuidate espero verte de nuevo"
        ], 
    2:["Soy un asistente virtual creado para ayudarte", 
        "¡Por supuesto! ¿con que necesitas ayuda?", 
        "Cuentame tu problema y buscaré solución",
        ],
    3:["Puedo ofrecerte información o resolver tus dudas", 
        "!En que te puedo ayudar",
        "Estoy aquí para resolver tus preguntas",
      ], 
    4:["¡Gracias a ti! ❤️", 
        "De nada, me alegra ser de ayuda", 
        "¡Muy amable de tu parte!"
        ], 
    5:["Lamento que te sientas así, puedo intentarlo de nuevo", 
        "Parece que algo no salió bien, ¿Quieres que lo revisemos?", 
        "No siempre soy perfecto",
        ]
} 

# --- Función de Fallback a Ollama ---
def get_ollama_response(user_text):
    """Llama a la API de Ollama para generar una respuesta genérica."""
    
    # Prepara el prompt para guiar al LLM
    prompt = f"El usuario dice: '{user_text}'. Responde de manera corta y útil como un asistente virtual."
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False # No usar streaming
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=45)
        response.raise_for_status() # Levanta HTTPError si la respuesta no fue 200 OK
        
        data = response.json()
        return data.get("response", "Lo siento, Ollama no pudo generar una respuesta clara.")

    except requests.exceptions.ConnectionError:
        error_msg = f"❌ Error de Conexión: Asegúrate de que Ollama esté corriendo en {OLLAMA_URL}."
        print(error_msg)
        return "No estoy seguro de entender, y mi asistente avanzado (Ollama) no está disponible en este momento. Intenta reformular."
    
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Error en la Petición a Ollama: {e}"
        print(error_msg)
        return "Hubo un error al procesar la respuesta avanzada. ¿Podrías intentar con una pregunta más simple?"

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.form.get("message", "")
    if not user_text.strip():
        return jsonify({"response": "Por favor escribe algo 😅"})

        # --- Activación manual de Ollama ---
    text_lower = user_text.lower()

    triggers = [
        "ollama",
        "llama",
        "hablar con ollama",
        "hablar con llama",
        "habla con ollama",
        "habla con llama"
    ]

    if any(t in text_lower for t in triggers):
        print("🔥 Trigger detectado, llamando a Ollama...")

        # Limpia todas las frases que activan el modo Ollama
        clean_text = text_lower
        for t in triggers:
            clean_text = clean_text.replace(t, "")

        clean_text = clean_text.strip()

        if not clean_text:
            clean_text = "dame un saludo"

        response = get_ollama_response(clean_text)
        return jsonify({"response": response})


    # --- Lógica de Respuesta Combinada (Clustering + Fallback) ---
    
    # Predice el grupo al que pertenece el mensaje (solo si el modelo se cargó)
    cluster = predict_cluster(model, vectorizer, user_text) if model else -1 

    # 1. Intenta usar la respuesta del clustering (si existe y el cluster es reconocido)
    if cluster in RESPUESTAS:
        # Se encontró un cluster conocido. Usamos la respuesta predefinida.
        response = random.choice(RESPUESTAS[cluster])
        print(f"Mensaje clasificado en Cluster {cluster}. Usando respuesta fija.")
    else:
        # 2. Caso de Fallback: Cluster no reconocido. Llamar a Ollama.
        print(f"Cluster {cluster} no reconocido o modelo de clustering no disponible. Recurriendo a Ollama...")
        response = get_ollama_response(user_text) # 👈 Llamada al LLM
        
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)