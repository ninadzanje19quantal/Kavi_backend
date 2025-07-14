1. Create a .env file and add teh following credentials to it

   1. Linkedin email id
   2. Linkedin password
   3. Gemini API key



2. Create a folder in backend_app/rag/knowledge_base
   and add the files that contain questions. These will be used to vectorize and build the knowledge base for our RAG part.



3. In vector_db.py only during the first time run the functions.
   1. read_csv_from_dir_into_txt _(Store the values and pass to next function)_
   2. create_embeddings_ids _(Store the values and pass to next function)_
   3. create_vectorDB
