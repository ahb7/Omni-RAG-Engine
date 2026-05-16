from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class PDFProcessor:
    def __init__(self):
        """
        Initialize the processor with optimized chunking parameters.
        Chunk size: 1000 characters (roughly 150-200 words)
        Chunk overlap: 100 characters (ensures context continuity between chunks)
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )

    def process_pdf(self, file_path: str):
        """
        Extracts text from a PDF and splits it into manageable chunks.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        try:
            # 1. Load the PDF
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            # 2. Split the document into chunks[cite: 1]
            # This maintains metadata (like page numbers) for each chunk
            chunks = self.text_splitter.split_documents(pages)
            
            print(f"📄 PDF Processed: {len(pages)} pages split into {len(chunks)} chunks.")
            return chunks

        except Exception as e:
            print(f"❌ Error processing PDF: {str(e)}")
            raise e


