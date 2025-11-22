import requests
import json

def debug_ollama():
    url = "http://localhost:11434/api/chat"
    
    # Simulate a large context
    context = "This is a test context. " * 500  # ~2500 characters
    
    system_message = (
        "You are a knowledgeable AI assistant specializing in analyzing documents. "
        "Your goal is to provide accurate, comprehensive answers based ONLY on the provided context. "
        "Always cite your sources using the format [Source X] at the end of sentences where information is used. "
        "If the context is insufficient, clearly state what is missing."
    )
    
    user_content = f"""Context information is below:
---------------------
{context}
---------------------

Using the context above, answer this question: What is this text about?"""

    messages = [
        {"role": "user", "content": system_message + "\n\n" + user_content}
    ]

    payload = {
        "model": "llama2:latest",
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 1024
        }
    }
    
    print(f"Sending request to {url}...")
    print(f"Payload size: {len(json.dumps(payload))} bytes")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse received:")
            # print(json.dumps(data, indent=2))
            
            content = data.get('message', {}).get('content', '')
            if not content:
                print("\n❌ ERROR: Answer is empty!")
            else:
                print(f"\n✅ SUCCESS: Answer received (length {len(content)})")
                print(content[:100] + "...")
        else:
            print(f"\n❌ Error: Status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")

if __name__ == "__main__":
    debug_ollama()
