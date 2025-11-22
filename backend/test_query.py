import requests
import json

def test_query():
    url = "http://localhost:8000/api/query/"
    payload = {
        "query": "What is the title of the document?",
        "top_k": 3
    }
    
    try:
        print(f"Sending query to {url}...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse received:")
            print(json.dumps(data, indent=2))
            
            if not data.get('answer'):
                print("\n❌ ERROR: Answer is empty!")
            else:
                print("\n✅ SUCCESS: Answer received.")
        else:
            print(f"\n❌ Error: Status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_query()
