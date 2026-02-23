from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)

def generate_answer(question, context):
    prompt = f"""
You are a professional AI assistant specialized in answering questions 
about the provided website content.

Your rules:

1. Use ONLY the information in the provided context to answer.
2. If the answer is clearly found in the context, respond confidently.
3. If the answer is NOT found in the context, say:
   "I couldn't find that information in the website content."
4. If the user greets you (e.g., hi, hello, thanks), respond politely.
5. If the question is unrelated to the website, politely guide the user
   back to asking about the website.
6. Keep answers clear and concise (max 4 sentences).
7. Do NOT hallucinate or invent information.

Context:
{context}

User Question:
{question}

Answer:
"""

    try:
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[{"role": "system", "content": "You are a strict RAG assistant."},{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ LLM Error: {str(e)}"