import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from src import embedding, generator, ingest

#Page Configuration
st.title(":red[RAG-Powered] PDF Q&A Assistant")
st.write("Upload your PDF document and ask questions about its content.")

#Client Definitions
load_dotenv()
client_ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_data")
ef = embedding_functions.GoogleGeminiEmbeddingFunction()


st.sidebar.header("Document Upload")
uploaded_files = st.sidebar.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files is not None:
    if st.sidebar.button("Process & Ingest All PDFs"):
        with st.spinner("Processing and embedding documents..."):

            os.makedirs("streamlit_data", exist_ok=True)
            success_count = 0

            for uploaded_file in uploaded_files:
                temp_pdf_path = os.path.join("streamlit_data", uploaded_file.name)

                try:
                    with open(temp_pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    context = ingest.load_pdf(file_path=temp_pdf_path, file_name=uploaded_file.name)
                    chunks = ingest.chunker(context)
                    embedding.record_documents(chroma_client, ef, "my_collection", chunks)
                    success_count += 1

                except Exception as e:
                    st.sidebar.error(f"Error with {uploaded_file.name}: {e}")

            if success_count > 0:
                st.sidebar.success(f"{success_count} PDF successfully ingested into ChromaDB!")

question = st.chat_input("Type your question here:")

if question:
    with st.spinner("AI is generating an answer..."):
        try:
            #Retrieve relevant chunks
            retrieved_chunks = embedding.query(chroma_client, ef, "my_collection", [question])
            if retrieved_chunks and retrieved_chunks[0]:
                #Create prompt
                prompt = generator.create_prompt(retrieved_chunks[0], question)
                
                #Generate answer from LLM
                answer = generator.generate_answer(prompt, client_ai, "gemini-3.5-flash")
                    
                # Display the result
                st.success("Answer:")
                st.write(answer)
            else:
                st.warning("No relevant context found in the database. Please ingest a PDF first or ask a related question.")
        except Exception as e:
            st.error(f"An error occurred: {e}")