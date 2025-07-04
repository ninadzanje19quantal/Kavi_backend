from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
from pathlib import Path
from chromadb.utils import embedding_functions
import chromadb

def read_csv_from_dir_into_txt(dir_path: str):
    csvs:  ... | None = Path(dir_path).iterdir()

    chunks = []
    # Create the splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,  # Customize depending on your model
        chunk_overlap=50  # Helps maintain context between chunks
    )

    for question_csv in csvs:

        # Your large text string
        doc_text = pd.read_csv(question_csv)
        doc_text = doc_text.apply(lambda row: ' '.join(row.values.astype(str)), axis=1).tolist()

        # Create the chunks
        chunks += text_splitter.create_documents(doc_text)

    return chunks

def create_embeddings_ids(chunks: list):
    #Configure the embedding function
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    #Create the documents i.e. Divide your main document into smaller chunks
    documents = []
    for chunk in chunks:
        documents.append(chunk.page_content)

    #Pass the documents to the embedding function to create embeddings
    embeddings = embedding_fn(documents)


    #Generate unique ids for each embedding. {len(ids) == len(embeddings)}

    ids = []
    for number in range(len(embeddings)):
        ids.append(str(number))

    return embeddings, ids, documents

def create_vectorDB(embeddings, ids, documents, db_path: str | None, collection_name: str):
    if isinstance(db_path, str):
        chroma_client = chromadb.PersistentClient(db_path)
    else:
        chroma_client = chromadb.PersistentClient()

    collection = chroma_client.get_or_create_collection(name=collection_name)

    collection.add(embeddings=embeddings, ids=ids, documents=documents)

