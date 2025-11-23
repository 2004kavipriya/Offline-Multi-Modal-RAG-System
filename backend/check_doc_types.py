import requests
import json

def check_documents():
    url = "http://localhost:8000/api/documents/"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            documents = response.json()
            print(f"\n{'='*80}")
            print(f"Found {len(documents)} document(s):")
            print(f"{'='*80}\n")
            
            images = []
            pdfs = []
            others = []
            
            for doc in documents:
                if doc['document_type'] == 'image':
                    images.append(doc)
                elif doc['document_type'] == 'pdf':
                    pdfs.append(doc)
                else:
                    others.append(doc)
            
            print(f"📄 PDFs: {len(pdfs)}")
            for pdf in pdfs:
                print(f"   - {pdf['filename']} ({pdf['num_chunks']} chunks)")
            
            print(f"\n🖼️  Images: {len(images)}")
            for img in images:
                print(f"   - {img['filename']}")
            
            print(f"\n📁 Others: {len(others)}")
            for other in others:
                print(f"   - {other['filename']} ({other['document_type']})")
            
            print(f"\n{'='*80}")
            
            if len(images) == 0:
                print("\n⚠️  No images found!")
                print("To show images, you need to:")
                print("1. Extract figures from PDFs and upload them as separate image files")
                print("2. Or use Cross-Modal search to find image-related content")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    check_documents()
