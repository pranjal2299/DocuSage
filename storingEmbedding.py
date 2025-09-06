from sentence_transformers import SentenceTransformer, util
import chromadb
import os
from langchain.schema import Document
import re
import fitz
from langchain_chroma import Chroma
# from langchain.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import shutil


def initialize_chroma_db(collection_name, embeddings, persist_directory):
    try:
        print("Trying to load existing Chroma DB...")
        vectorDB = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )
        print("Chroma DB loaded successfully.")
        return vectorDB
    except Exception as e:
        print(f"Error loading Chroma DB: {e}")
        print("Deleting corrupted persist directory and rebuilding...")
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
        # Recreate
        vectorDB = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )
        print("New Chroma DB created.")
        return vectorDB

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        if os.path.exists(pdf_file):
            doc = fitz.open(pdf_file)
            text = ""
            for page in doc:
                text += page.get_text("text")
            return text
        else:
            print("No pdf file exists by this name.")
    except Exception as e:
        print(e)

# Function to clean symbols using regex
def applying_symbol_regex(text):
    remove_symbols_text = re.sub(r"""[,._/?''"";{}\-*&^%$#@!,\\|()+=`~<>]""", "", text)
    return remove_symbols_text

# Function to clean whitespaces
def clean_text(input_text):
    cleaned_text = re.sub(r"\s+ ", " ", input_text)
    cleaned_text = cleaned_text.strip()
    clean_text = cleaned_text.replace("\n", "")
    return clean_text

# Main processing function
def process_pdf(docId,pdf_file_path, collection_name="embeddings", persist_directory="./MM_CHROMA_DB"):
    print(docId)
    # Extract text from the PDF
    pdf_result = extract_text_from_pdf(pdf_file_path)

    # Apply regex to remove symbols
    regex_result = applying_symbol_regex(pdf_result)

    # Clean text result
    clean_text_result = clean_text(regex_result)
    print("Total tokens without symbols  in a PDF => ", len(clean_text_result))
    
    document = Document(page_content=clean_text_result)
    print("came here")
    # Splitting the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=30)
    chunks = text_splitter.split_documents([document])

    # Set up the embedding function
    model_kwargs = {"device": "mps"}
    encode_kwargs = {"normalize_embeddings": True}
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-distilroberta-base-v1",
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    print("beore vectorDB")
    print("persist_directory exists:", os.path.exists(persist_directory))

    # Set up the Chroma database
    vectorDB = initialize_chroma_db(collection_name, embeddings, persist_directory)
    print("after vectorDB")

    metadata_chunks = []
    # Concatenate all chunks into a single string
    for i, chunk in enumerate(chunks):
        # Add metadata to each chunk
        metadata = {"source": f"example_source_{i}", "docId":str(docId)}
        id = str(i)
        doc_with_metadata = Document(
            page_content=chunk.page_content, metadata=metadata, id=id,docId=docId
        )
        metadata_chunks.append(doc_with_metadata)
 
    print("Done")

    # Add the documents to the vector database
    try:
        vectorDB.add_documents(metadata_chunks)
    except:
        raise Exception()
    
    # for i, chunk in enumerate(chunks):
    #     metadata = {"source": f"example_source_{i}"}
        
    #     # Use the same document ID for all chunks
    #     doc_with_metadata = Document(
    #         page_content=chunk.page_content, metadata=metadata, id=docId
    #     )
    #     print(f"Chunk {i} => {chunk.page_content}")
    #     print("\n")


    print("Documents have been added to the vector database.")
