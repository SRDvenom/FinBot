from calculators import handle_financial_calculations
from finance_data import handle_stock_queries

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment (from .env via load_dotenv above)
api_key = os.environ.get("GOOGLE_API_KEY")
GEMINI_CONFIGURED = False
if not api_key:
    print("Warning: GOOGLE_API_KEY not found in environment variables. Gemini AI will be disabled until the key is provided in .env or the environment.")
else:
    try:
        # Some versions of the google.generativeai library expect genai.configure
        # while others provide different client surfaces. We attempt configure() if available.
        if hasattr(genai, 'configure'):
            genai.configure(api_key=api_key)
            GEMINI_CONFIGURED = True
        else:
            # Try set environment variable as a fallback for SDKs that read from env
            os.environ['GOOGLE_API_KEY'] = api_key
            GEMINI_CONFIGURED = True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        GEMINI_CONFIGURED = False


def create_financial_advice_prompt(user_question):
    """
    Creates a simplified prompt for the Gemini model for a direct chat.
    """
    prompt = f"""You are a helpful and knowledgeable financial advisor.
    The user's question is: {user_question}
    Provide a helpful and concise response.
    """
    return prompt

def get_financial_advice(question):
    """Provides financial advice using the configured Gemini model.

    This function is defensive about the SDK version and will:
      - return a helpful message if the API key is not configured
      - try several common SDK call patterns and fall back gracefully
    """
    if not GEMINI_CONFIGURED:
        return "AI model not configured. Please set GOOGLE_API_KEY in your .env or environment to enable Gemini responses."

    prompt = create_financial_advice_prompt(question)

    try:
        # Preferred: high-level helper (older/newer SDKs may expose different helpers)
        if hasattr(genai, 'generate_text'):
            # generate_text often returns an object with a .text attribute or a dict
            resp = genai.generate_text(model='gemini-pro-latest', prompt=prompt)
            # try common shapes
            if hasattr(resp, 'text'):
                return resp.text
            if isinstance(resp, dict):
                # common dict shapes: {'candidates': [{'output': '...'}]} or {'text': '...'}
                if resp.get('text'):
                    return resp.get('text')
                candidates = resp.get('candidates') or []
                if candidates and isinstance(candidates, list):
                    first = candidates[0]
                    return first.get('content') or first.get('output') or str(first)
                return str(resp)

        # Alternative: object-oriented GenerativeModel (some SDK versions)
        if hasattr(genai, 'GenerativeModel'):
            model = genai.GenerativeModel('gemini-pro-latest')
            # generate_content may return an object with .text
            response = model.generate_content(prompt)
            if hasattr(response, 'text'):
                return response.text
            # attempt to stringify
            return str(response)

        # As a last resort, try a generic 'generate' if present
        if hasattr(genai, 'generate'):
            resp = genai.generate(model='gemini-pro-latest', prompt=prompt)
            if isinstance(resp, dict):
                return resp.get('text') or str(resp)
            return str(resp)

        # If we reach here, the SDK surface is unexpected
        return "Gemini SDK is present but in an unexpected state; unable to call the model."

    except Exception as e:
        print(f"Error generating content: {e}")
        return "Sorry, I am having trouble generating a response right now."
# --- Flask App ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400


    # Try to handle special queries first (calculations or stock data)
    calc_response = handle_financial_calculations(user_message)
    if calc_response:
        return jsonify({"response": calc_response})

    stock_response = handle_stock_queries(user_message)
    if stock_response:
        return jsonify({"response": stock_response})

    # Otherwise, use Gemini
    bot_response = get_financial_advice(user_message)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True, port=5001)