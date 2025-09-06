import chromadb
import os
from langchain_chroma import Chroma
from chromadb.config import  DEFAULT_DATABASE, DEFAULT_TENANT
import time
import transformers
from langchain_community.llms import CTransformers
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from transformers import pipeline
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama









client = chromadb.HttpClient("http://localhost:8000")


def using_ollama_model(retriever, query, results,conversation_history):

    history_text = ""
    for item in conversation_history:
        if "question" in item and item["question"]:
            history_text += f"User: {item['question']}\n"
        if "answer" in item and item["answer"]:
            history_text += f"Assistant: {item['answer']}\n"

    print("<<<<<< LLM MODEL STARTED >>>>>>")
    print(" ========>", history_text)
    # Ensure the prompt template is well-structured
    prompt_template = """
    You are a helpful assistant. Answer the following question using the provided context and previous conversation history.
    If the context does not contain the answer, only then reply with: "Sorry, I don't have enough information."
    Conversation History :{history} 
    Context:{results}
    Question:{query}
    """

    # Initialize the PromptTemplate

    template = PromptTemplate(
        input_variables=["history","results", "query"], template=prompt_template,
    )

    doc_texts = "\\n".join([doc.page_content for doc in results])

    formatted_output = template.format(history=history_text,results=doc_texts, query=query)

    print("<<<<<<<<<<< Formatted Output >>>>>>>>>>>")
    print(formatted_output)
    print("type of formatted output is ", type(formatted_output))


    llm = ChatOllama(model="llama3.2", temperature=0.4, num_predict=512)

    rag_chain = template | llm | StrOutputParser()

    # results = retriever.invoke(query)
    # doc_texts = "\\n".join([doc.page_content for doc in results])

    answer = rag_chain.invoke({"history" : history_text,"results": doc_texts, "query": query})

    return answer

    # # Set up the RAG pipeline
    # rag_pipeline = RetrievalQAWithSourcesChain.from_chain_type(
    #     llm=llm, chain_type="stuff", retriever=retriever
    # )
    #
    # try:
    # #     # answer = rag_pipeline.run(formatted_output)
    #     answer = rag_pipeline.invoke(formatted_output)
    #     return answer
    # except Exception as e:
        # print(f"Error occurred during invocation: {e}")
        # return None






def retrievingReponse(docId, query, conversation_history) :
    
    model_kwargs = {"device": "mps"}
    encode_kwargs = {"normalize_embeddings": True}
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-distilroberta-base-v1",
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )

    vectorDB = Chroma(
        collection_name="embeddings",
        embedding_function=embeddings,  # Using the encode method to get embeddings
        persist_directory="MM_CHROMA_DB",
    )

    # retriever = vectorDB.as_retriever(
    # search_type="mmr",
    # search_kwargs={
    #     "k": 6, # was 5 originally
    #     "lambda_mult": 1, # was 0.30 originally
    #     "filter": {"docId": docId}
    # }
    # )
    retriever = vectorDB.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 4, # was 5 originally
        # "lambda_mult": 1, # was 0.30 originally
        "filter": {"docId": docId}
    }
    )

      # retriever = vectorDB.as_retriever()
    print("<<<<<<<<<<<<<<<< Retriever >>>>>>>>>>>>>>>>")
    # print("d",retriever)
    print("\n")

    results = retriever.invoke(
        query
    ) 

    unique_results = []
    seen_texts = set()

    for result in results:
        print(result)
        # If the result's content has not been seen before, process it
        if result.page_content not in seen_texts:
            ans = result.page_content
            ans = ans.replace("\n", "")  # Clean the content by removing newlines
            unique_results.append(ans)  # Add the cleaned answer to the results list
            seen_texts.add(result.page_content)  # Mark this text as seen

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    start = time.time()

    # llm_result = using_llm_model(retriever, query, results)
    llm_result = using_ollama_model(retriever, query, results, conversation_history)
    end = time.time()
    print("Inference Time:>>>>>>> ", end - start)
    return llm_result

