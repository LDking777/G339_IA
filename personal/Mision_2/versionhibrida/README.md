# convertir tu chatbot en una aplicación web funcional (con interfaz web y backend) y desplegarla fácilmente en Render
🚀 OBJETIVO

✅ Convertir tu chatbot en una aplicación web
✅ Crear una interfaz HTML simple
✅ Configurar Render para desplegarlo
✅ Que responda directamente desde el navegador

version4
    chatbot
        __init__.py    <!-- Archivo vacío que permite tratar la carpeta como un paquete Python -->
        data.py
        model.py
    models  carpeta vacía donde se crean los modelos
    templates
        index.html
    main.py
    README.md 
    requirements.txt   al final lo generamos pip freeze > requirements.txt 


1) hatbot/model.py

 funciones para guardar, cargar y predecir
```
 # chatbot/model.py
import os
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
ANSWERS_PATH = os.path.join(MODEL_DIR, "answers.pkl")


def build_and_train_model(train_pairs):
    """
    Entrena el modelo con las preguntas y respuestas proporcionadas.
    """
    questions = [q for q, _ in train_pairs]
    answers = [a for _, a in train_pairs]

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(questions)

    unique_answers = sorted(set(answers))
    answer_to_label = {a: i for i, a in enumerate(unique_answers)}
    y = [answer_to_label[a] for a in answers]

    model = MultinomialNB()
    model.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(ANSWERS_PATH, "wb") as f:
        pickle.dump(unique_answers, f)

    print("✅ Modelo entrenado y guardado correctamente.")
    return model, vectorizer, unique_answers


def load_model():
    """
    Carga el modelo, el vectorizador y las respuestas si existen.
    """
    if (
        os.path.exists(MODEL_PATH)
        and os.path.exists(VECTORIZER_PATH)
        and os.path.exists(ANSWERS_PATH)
    ):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            vectorizer = pickle.load(f)
        with open(ANSWERS_PATH, "rb") as f:
            unique_answers = pickle.load(f)
        print("📂 Modelo cargado desde disco.")
        return model, vectorizer, unique_answers
    else:
        print("⚠️ No hay modelo guardado. Será necesario entrenarlo.")
        return None, None, None


def predict_answer(model, vectorizer, unique_answers, user_text):
    """
    Predice una respuesta según el texto del usuario.
    """
    X = vectorizer.transform([user_text])
    label = model.predict(X)[0]
    return unique_answers[label]


```

2) chatbot/data.py
   
```
# chatbot/data.py

training_data = [
    ("hola", "¡Hola! ¿En qué puedo ayudarte?"),
    ("buenos días", "¡Buenos días!"),
    ("cómo estás", "Estoy bien, gracias por preguntar."),
    ("adiós", "¡Hasta luego!"),
    ("tu nombre", "Soy un chatbot de ejemplo."),
    ("qué puedes hacer", "Puedo responder preguntas simples basadas en ejemplos."),
]


```
3) main.py — versión Flask

Este archivo ahora servirá como servidor web.
```
# main.py
from flask import Flask, render_template, request, jsonify
from chatbot.data import training_data
from chatbot.model import build_and_train_model, load_model, predict_answer

app = Flask(__name__)

# Intentamos cargar el modelo (o entrenamos si no existe)
model, vectorizer, unique_answers = load_model()
if model is None:
    model, vectorizer, unique_answers = build_and_train_model(training_data)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.form.get("message", "")
    if not user_text.strip():
        return jsonify({"response": "Por favor escribe algo 😅"})

    response = predict_answer(model, vectorizer, unique_answers, user_text)
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

```

4) templates/index.html
```
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Chatbot Inteligente</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f2f4f8;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    #chatbox {
      background: white;
      width: 400px;
      border-radius: 15px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
      padding: 20px;
      display: flex;
      flex-direction: column;
    }
    #messages {
      flex-grow: 1;
      overflow-y: auto;
      margin-bottom: 15px;
    }
    .msg { margin: 8px 0; }
    .user { text-align: right; color: blue; }
    .bot { text-align: left; color: green; }
    input[type="text"] {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 10px;
      outline: none;
    }
  </style>
</head>
<body>
  <div id="chatbox">
    <h2>🤖 Chatbot</h2>
    <div id="messages"></div>
    <form id="chatForm">
      <input type="text" id="userInput" placeholder="Escribe tu mensaje..." autocomplete="off" />
    </form>
  </div>

  <script>
    const form = document.getElementById("chatForm");
    const input = document.getElementById("userInput");
    const messages = document.getElementById("messages");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      messages.innerHTML += `<div class="msg user">Tú: ${text}</div>`;
      input.value = "";

      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `message=${encodeURIComponent(text)}`
      });

      const data = await response.json();
      messages.innerHTML += `<div class="msg bot">Bot: ${data.response}</div>`;
      messages.scrollTop = messages.scrollHeight;
    });
  </script>
</body>
</html>

```

## librerias 
Revisé  con pip list que librerías tiene instalados y si le falta alguna de estas instale  
| Libreria | comado                   |
| -------- | ------------------------ |
| Flask    | pip install flask        |
| sklearn  | pip install scikit-learn |
| pandas   | pip install pandas       |
| gunicorn   | pip install gunicorn       |

cree un archivo Procfile

Este archivo le indica a Render cómo ejecutar
```
web: gunicorn main:app
```
puedes probar local mente  python main.py
para render crear un requirements.txt solo con lo que se necesita ejemplo
```
Flask==3.1.1
joblib==1.5.1
pandas==2.3.1
scikit-learn==1.7.1
gunicorn
```
Desplegar en Render
Paso a paso:

Crea un repositorio en GitHub con todos estos archivos.

Sube tu proyecto.

Entra a https://render.com
 y crea una cuenta.

Clic en “New +” → “Web Service”.

Conecta tu repositorio.
Render detectará automáticamente el requirements.txt y el Procfile.

Configura:

Runtime: Python 3.x

Build Command: pip install -r requirements.txt

Start Command: gunicorn main:app

Espera que Render construya e inicie tu app 🌐