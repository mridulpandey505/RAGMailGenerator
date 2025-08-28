import uuid
import chromadb
from PyPDF2 import PdfReader

class ResumePortfolio:
    def __init__(self, persist_dir="vectorstore"):
        self.chroma_client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.chroma_client.get_or_create_collection(name="resume_portfolio")

    def _load_pdf(self, file_path):
        
        reader = PdfReader(file_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            
        return text.strip()

    def _chunk_text(self, text, chunk_size=400, overlap=50):
        
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    def load_resume(self, file_path):
        
        if not self.collection.count():
            
            text = self._load_pdf(file_path)
            chunks = self._chunk_text(text)

            for chunk in chunks:
                self.collection.add(
                    documents=[chunk],
                    metadatas={"source": file_path},
                    ids=[str(uuid.uuid4())]
                )
            

    def query_resume(self, query: str, n_results=3):
        """Query resume for relevant info"""
        print(f"🔍 Query: {query}")
        results = self.collection.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        return docs

        


if __name__ == "__main__":
    portfolio = ResumePortfolio()
    portfolio.load_resume("resume.pdf")
    results = portfolio.query_resume("What are the positions of responsibility ?")
    print(results)
    
    