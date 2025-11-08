from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

def build_and_train_model(train_pairs):
    questions = [q for q, _ in train_pairs]
    answers = [a for _, a in train_pairs]
    vectorizer = CountVectorizer()
    x = vectorizer.fit_transform(questions)

    unique_answer = sorted(set(answers))
    answer_to_label = {a: i for i, a in enumerate(unique_answer)}
    y = [answer_to_label[a] for a in answers]

    model = MultinomialNB()
    model.fit(x, y)

    return model, vectorizer, unique_answer

def predict_answer(model, vectorizer, unique_answer, user_text):
    x = vectorizer.transform([user_text])
    label = model.predict(x)[0]
    return unique_answer[label]

if __name__ == "__main__":
    training_data = [
    """     ("hola", "¡Hola! ¿En qué puedo ayudarte?"),
        ("buenos dias", "¡Buenos días!"),
        ("cómo estás", "Estoy bien, gracias por preguntar."),
        ("adiós", "¡Hasta luego!"),
        ("tu nombre", "Soy un chatbot de ejemplo."),
        ("que puedes hacer", "Puedo responder preguntas simples basadas en ejemplos.") """
    ]

    model, vectorizer, unique_answer = build_and_train_model(training_data)
    print("Chatbot supervisado listo. Escribe 'salir' para terminar.")

    while True:
        user = input("Tú: ").strip()
        if user.lower() in {"salir", "exit", "quit"}:
            print("Bot: ¡Hasta pronto!")
            break
        response = predict_answer(model, vectorizer, unique_answer, user)
        print("Bot:", response)
