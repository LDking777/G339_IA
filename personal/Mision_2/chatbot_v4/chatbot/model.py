import os 
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB 

MODEL_DIR="models" 
MODEL_PATH=os.path.join(MODEL_DIR,"model.pkl")
VECTORIZER_PATH=os.path.join(MODEL_DIR,"vectorizer.pkl")
ANSWER_PATH=os.path.join(MODEL_DIR,"answer.pkl") 

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
    #Crear una carpeta modelo si no existe
    os.makedirs(MODEL_DIR, exist_ok=True)
    #Guardar el modelo          
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f) 
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(ANSWER_PATH, "wb") as f:
        pickle.dump(unique_answer, f)
    print("Modelo entrenado y guardado exitosamente.")
    #guardar el vectorizador
    return model, vectorizer, unique_answer 

def load_model():
    if (
        os.path.exists(MODEL_PATH)
        and os.path.exists(VECTORIZER_PATH)
        and os.path.exists(ANSWER_PATH)
    ):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            vectorizer = pickle.load(f)
        with open(ANSWER_PATH, "rb") as f:
            unique_answer = pickle.load(f)
        print("Modelo cargado exitosamente.")
        return model, vectorizer, unique_answer
    else:
        print("No hay modelo guardado, será necesario entrenarlo.")
        return None, None, None
       
def predict_answer(model, vectorizer, unique_answer, user_text):
    x = vectorizer.transform([user_text])
    label = model.predict(x)[0]
    return unique_answer[label]