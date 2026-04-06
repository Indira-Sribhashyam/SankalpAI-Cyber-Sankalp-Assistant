import json
import time
import asyncio
import os
from datasets import Dataset

# For Ragas with Groq and HuggingFace
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# Import existing functions from your API
from assistant_api import retrieve_context, run_llm, groq_key

# Set up evaluation wrappers
if not groq_key:
    print("GROQ_API_KEY is not set. Cannot run evaluation.")
    exit(1)

eval_llm = LangchainLLMWrapper(ChatGroq(api_key=groq_key, model="llama-3.1-8b-instant"))
eval_embeddings = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

async def run_evaluation():
    print("Loading test dataset...")
    with open("eval_dataset.json", "r") as f:
        tests = json.load(f)
        
    data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}
    
    print(f"Running pipeline for {len(tests)} queries...")
    for t in tests:
        start_time = time.time()
        
        # 1. Retrieve Context
        ctx_docs = retrieve_context(t["question"], k=5)
        contexts = [d["content"] for d in ctx_docs]
        
        # 2. Run LLM
        system_prompt = "You are SecAI, an advanced assistant for CCTV security. Use the provided context to answer."
        user_prompt = f"Context:\n{contexts}\n\nUser Query: {t['question']}"
        answer = await run_llm(system_prompt, user_prompt)
        
        latency = time.time() - start_time
        print(f"Query: '{t['question']}' | Latency: {latency:.2f}s")
        
        data["question"].append(t["question"])
        data["answer"].append(answer)
        data["contexts"].append(contexts)
        data["ground_truth"].append(t["ground_truth"])
        
    # 3. Evaluate with Ragas
    print("Starting Ragas evaluation... (This may take a minute)")
    dataset = Dataset.from_dict(data)
    results = evaluate(
        dataset,
        metrics=[context_precision, context_recall, answer_relevancy],
        llm=eval_llm,
        embeddings=eval_embeddings,
        raise_exceptions=False
    )
    
    print("\n=== Evaluation Results ===")
    print(results)
    
if __name__ == "__main__":
    asyncio.run(run_evaluation())
