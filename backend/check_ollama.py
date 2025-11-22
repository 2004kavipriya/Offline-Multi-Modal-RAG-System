import requests
import json

def check_ollama():
    url = "http://localhost:11434/api/tags"
    try:
        print(f"Checking Ollama API at {url}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Ollama is running!")
            print("Available models:")
            models = [model['name'] for model in data.get('models', [])]
            for model in models:
                print(f" - {model}")
                
            if not models:
                print("\n⚠️ No models found! You need to run 'ollama pull <model_name>'")
        else:
            print(f"\n❌ Error: Status code {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to Ollama! Is it running?")
        print("Try running 'ollama serve' or opening the Ollama app.")
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")

if __name__ == "__main__":
    check_ollama()
