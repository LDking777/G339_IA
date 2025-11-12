from flask import Flask, render_template, request, jsonify
from chatbot.data import training_data 
from chatbot.model import build_and_train_model, predict_answer, load_model 

app = Flask(__name__)

model, vectorizer, unique_answer = load_model()
if model is None: 
    model, vectorizer, unique_answer = build_and_train_model(training_data)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/chat', methods=['POST']) 
def chat():
    user_text = request.form.get('message',"") 
    if not user_text.strip(): 
        return jsonify({"response": "Porfavor escriba algo 😂"}) 
    response = predict_answer(model, vectorizer, unique_answer, user_text) 
    return jsonify({"response": response})
    



def chat(model, vectorizer, unique_answer): 
    """Inicia el modelo de conversación"""
    print("\n 💭 Chat inciado. Escribe 'salir' para terminar.")
    
    while True:
        user = input("Tú: ").strip()
        if user.lower() in {"salir", "exit", "quit"}:
            print("Bot: ¡Hasta pronto!")
            break
        response = predict_answer(model, vectorizer, unique_answer, user)
        print("Bot:", response)


def main():
    model, vectorizer, unique_answer = load_model()

    while True:
        print("\n=== 🤖 MENÚ PRINCIPAL DEL CHATBOT ===")
        print("1️⃣  Chatea con el modelo")
        print("2️⃣  Reentrenar el modelo")
        print("3️⃣  Salir")

        opcion = input("\nElige una opción (1-3): ").strip()

        if opcion == "1":
            if model is not None:
                chat(model, vectorizer, unique_answer)
            else:
                print("\n⚠️ No hay modelo cargado. Entrénalo primero con la opción 2.")
        
        elif opcion == "2":
            print("\n🔄 Reentrenando el modelo con los nuevos datos...")
            model, vectorizer, unique_answer = build_and_train_model(training_data)
            print("\n✅ Modelo reentrenado exitosamente.")
        
        elif opcion == "3":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("\n❌ Opción no válida. Intenta nuevamente.")
    

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000)