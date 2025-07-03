from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd

# Your large text string
doc_text = pd.read_csv("knowledge_base/Designer Interview Questions - Questions.csv")
doc_text = doc_text.apply(lambda row: ' '.join(row.values.astype(str)), axis=1).tolist()

# Create the splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,       # Customize depending on your model
    chunk_overlap=50      # Helps maintain context between chunks
)

# Create the chunks
chunks = text_splitter.create_documents(doc_text)

doc_text = pd.read_csv("knowledge_base/Product Manager Interview Questions - Sheet1.csv")
doc_text = doc_text.apply(lambda row: ' '.join(row.values.astype(str)), axis=1).tolist()

chunks += text_splitter.create_documents(doc_text)


from chromadb.utils import embedding_functions

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

import chromadb
chroma_client = chromadb.PersistentClient()

collection = chroma_client.get_or_create_collection(name="work-role-vectorDB")

collection.add(embeddings=embeddings, ids=ids, documents=documents)
