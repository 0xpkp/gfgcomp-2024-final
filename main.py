# python application using flask
from flask import Flask, render_template, request, jsonify
import openai
from pickle import load
from sklearn.preprocessing import StandardScaler


# initialising application
app = Flask(__name__)




API_KEY = "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"
client = openai.OpenAI(api_key=API_KEY)

# to save chat history
chat_history = ""

# loading interface at root
@app.route("/")
def index():
    return render_template("index.html")

# Route for the chat page
@app.route("/chat.html")
def chat():
    return render_template("chat.html")

# Route for the heart_disease_detection page
@app.route("/heart_disease_detection.html")
def heart():
    return render_template("heart_disease_detection.html")

# Route for the kidney_disease_detection page
@app.route("/kidney_disease_detection.html")
def kidney():
    return render_template("kidney_disease_detection.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    global chat_history

    try:
        user_input = request.form.get("user_input")

        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""you are Lisa, a AI Chatbot designed and developed by Praveen, to have human like conversation with mentally ill patients. your missions is to have supporting conversation with the user and help the user with mental illness. you have to respond according to the chat history provided below. if the chat history is empty, consider that it is the start of a new conversation.
                Once the user starts to interact, you ask few questions asking the user about the common symptoms of depression.
                {chat_history}
        """,
            },
            {"role": "user", "content": f"{user_input}"},
        ],
    )
        
        # getting the response from api
        bot_response = response.choices[0].message.content

        # update chat history
        chat_history += f"User: {user_input}\nChatbot: {bot_response}\n"
        

        return jsonify({"bot_response": bot_response})

# handling the exception
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"Internal Server Error: {e}"}), 500

# response for heart disease detection
@app.route("/heart_disease_detection_submit", methods=["POST"])
def heart_disease_detection_submit():
    try:
        data = request.json
        result = heart_response(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def heart_response(data):
    try:
        
        values = [[data['age'], data['sex'],  data['cp'], data['trestbps'], data['chol'], data['fbs'], data['restecg'], data['thalach'], data['exang'], data['oldpeak'], data['slope'], data['ca'], data['thal']]]
        scaler = StandardScaler()
        values = scaler.fit_transform(values)

        model = load(open(r"model_heart.pkl", 'rb'))
        prediction = model.predict(values) * 100
        print("Prediction:", prediction)  # Print the prediction value for debugging

        # Return the prediction as a JSON object with 'result' key
        return {"result": prediction.tolist()}
    except Exception as e:
        print("Error in heart_response:", e)
        raise  # Reraise the exception to see the full traceback in the console


# Load the kidney disease model and scaler
def load_kidney_model():
    # Replace these paths with the actual paths to your kidney disease model and scaler
    model_path = r"model_kidney.pkl"
    model = load(open(model_path, 'rb'))
    
    return model

# Load kidney disease model and scaler
kidney_model = load_kidney_model()

# Route to handle kidney disease detection
@app.route("/kidney_response", methods=["POST"])
def kidney_response():
    try:
        # Get data from the frontend
        data = request.json
        
        # Process the data using the kidney disease model
        result = kidney_disease_detection(data)
        
        # Return the result as JSON
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to perform kidney disease detection
def kidney_disease_detection(data):
    try:
        # Transform input data using the loaded scaler
        scaler = StandardScaler()
        values = scaler.fit_transform([data['age'], data['bp'], data['sg'], data['al'], data['su'], data['rbc'], data['pc'], data['pcc'], data['ba'], data['bgr'], data['bu'], data['sc'], data['sod'], data['pot'], data['hemo'], data['pcv'], data['wc'], data['rc'], data['htn'], data['dm'], data['cad'], data['appet'], data['pe'], data['ane']])
        
        # Make predictions using the kidney disease model
        prediction = kidney_model.predict(values) * 100
        
        print("Prediction:", prediction)  # Print the prediction value for debugging

        # Return the prediction as a JSON object with 'result' key
        return {"result": prediction.tolist()}
        
    except Exception as e:
        return str(e)
    
if __name__ == "__main__":
    app.run(debug=True)
