import requests
import json

def test_documents_api():
    url = "http://localhost:8000/api/documents/"
    
    try:
        print(f"Fetching documents from {url}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            documents = response.json()
            print(f"\n✅ Found {len(documents)} document(s):\n")
            print("="*80)
            
            for i, doc in enumerate(documents, 1):
                print(f"\n{i}. {doc['filename']}")
                print(f"   ID: {doc['document_id']}")
                print(f"   Type: {doc['document_type']}")
                print(f"   Size: {doc['file_size']:,} bytes")
                print(f"   Chunks: {doc['num_chunks']}")
                print(f"   Uploaded: {doc['upload_date']}")
                print(f"   Processed: {'✅ Yes' if doc['processed'] else '❌ No'}")
            
            print("\n" + "="*80)
        else:
            print(f"\n❌ Error: Status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_documents_api()
