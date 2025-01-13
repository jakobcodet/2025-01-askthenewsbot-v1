import requests
import re

# API key for the Perplexity API, get your own at https://perplexity.ai
api_key = "your_key"

def make_perplexity_api_call(
    api_key: str,
    model: str,
    user_message: str
) -> dict:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.2,
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Example usage
def getAnswer(current_news, question):
    # make a prompt including the current_news from the main script and the user's question
    prompt = f"Folgende Informationen habe ich schon:\n\n{current_news} \n\nDazu möchte ich jetzt folgendes wissen, bitte kurz auf 5 Zeilen zusammengefasst:\n{question}"
    print(prompt)
    response = make_perplexity_api_call(api_key, "llama-3.1-sonar-large-128k-online", prompt)
    # Remove all square brackets and their contents from the answer
    answer = re.sub(r'\[.*?\]', '', response['choices'][0]['message']['content']).strip()
    print(f"Antwort in PerplexityStuff:\n{answer}")
    return answer


def getEasyAnswer(current_news, question):
    # make a prompt asking for easy language, including the current_news from the main script and the user's question
    prompt = f"Folgende Informationen habe ich schon:\n\n{current_news} \n\nDazu möchte ich jetzt folgendes wissen, bitte auf 5 Sätzen zusammengefasst. Bitte in leicht verständlicher Sprache, auf dem Sprachniveau eines 12-Jährigen Schülers. Ersetze Fremdwörter durch einfache Worte und nutze nur Hauptsätze. Formuliere Abkürzungen immer aus.\n\nHier steht meine Frage:\n{question}"
    print(prompt)
    response = make_perplexity_api_call(api_key, "llama-3.1-sonar-large-128k-online", prompt)
    # Remove all square brackets and their contents from the answer
    answer = re.sub(r'\[.*?\]', '', response['choices'][0]['message']['content']).strip()
    print(f"Antwort in PerplexityStuff:\n{answer}")
    return answer