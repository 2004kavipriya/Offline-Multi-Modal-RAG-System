import requests
import json

def test_ollama_direct():
    url = "http://localhost:11434/api/generate"
    
    prompt = """[INST] <<SYS>>
You are a helpful AI assistant.
<</SYS>>

Answer this question: What is the capital of France?
[/INST]"""

    payload = {
        "model": "mistral:latest",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 1024
        }
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse received:")
            print(json.dumps(data, indent=2))
            
            answer = data.get('response', '')
            if not answer:
                print("\n❌ ERROR: Answer is empty!")
            else:
                print(f"\n✅ SUCCESS: Answer: {answer}")
        else:
            print(f"\n❌ Error: Status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_ollama_direct()
