import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

DOCS_DIR = "./documents"
VECTORDB_DIR = "./chroma_db"

def build_vector_store():
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"Created '{DOCS_DIR}' directory. Place your .txt or .pdf files here.")
        return

    print("Loading documents...")
    text_loader = DirectoryLoader(DOCS_DIR, glob="*.txt", loader_cls=TextLoader)
    pdf_loader = DirectoryLoader(DOCS_DIR, glob="*.pdf", loader_cls=PyPDFLoader)
    
    docs = text_loader.load() + pdf_loader.load()

    if not docs:
        print("No documents found in ./documents folder.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    print(f"Split {len(docs)} document(s) into {len(chunks)} text chunks.")

    print("Generating local embeddings using nomic-embed-text...")
    # Use dedicated embedding model
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORDB_DIR
    )
    print("Vector database built successfully!")

if __name__ == "__main__":
    build_vector_store()