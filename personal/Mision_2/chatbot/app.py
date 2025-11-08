from flask import Flask, render_template, request, jsonify
from chatbot_supervisado import build_and_train_model, predict_answer

app = Flask(__name__)

# Entrena tu modelo (puedes hacerlo aquí o cargar uno entrenado)
training_data = [
    ("hola", "¡Hola! ¿En qué puedo ayudarte?"),
    ("buenos dias", "¡Buenos días!"),
    ("cómo estás", "Estoy bien, gracias por preguntar."),
    ("adiós", "¡Hasta luego!"),
    ("tu nombre", "Soy un chatbot de ejemplo."),
    ("que puedes hacer", "Puedo responder preguntas simples basadas en ejemplos.")
]

model, vectorizer, unique_answer = build_and_train_model(training_data)

@app.route("/")
def index():
    return render_template("chat_vista.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json["message"]
    bot_reply = predict_answer(model, vectorizer, unique_answer, user_input)
    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
