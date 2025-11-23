"""
Script to list all uploaded documents from the database.
"""
from sqlalchemy import create_engine, text
from app.config import get_settings

def list_documents():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Get all documents
        result = conn.execute(text("""
            SELECT 
                id,
                filename,
                document_type,
                file_size,
                upload_date,
                processed,
                minio_path
            FROM documents
            ORDER BY upload_date DESC
        """))
        
        documents = result.fetchall()
        
        if not documents:
            print("No documents found in the database.")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(documents)} document(s):")
        print(f"{'='*80}\n")
        
        for i, doc in enumerate(documents, 1):
            print(f"{i}. {doc.filename}")
            print(f"   ID: {doc.id}")
            print(f"   Type: {doc.document_type}")
            print(f"   Size: {doc.file_size:,} bytes")
            print(f"   Uploaded: {doc.upload_date}")
            print(f"   Processed: {'✅ Yes' if doc.processed else '❌ No'}")
            print(f"   MinIO Path: {doc.minio_path}")
            print()

if __name__ == "__main__":
    list_documents()
