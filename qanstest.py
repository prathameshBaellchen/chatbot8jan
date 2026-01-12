import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
import openai
from dotenv import load_dotenv
load_dotenv()

# Set SSL cert paths if cacert.pem exists
cacert_path = os.path.join(os.path.dirname(__file__), "cacert.pem")
if os.path.exists(cacert_path):
    os.environ["SSL_CERT_FILE"] = cacert_path
    os.environ["REQUESTS_CA_BUNDLE"] = cacert_path

# Lazy initialization - don't check API key at import time
OPENAI_KEY = None
db = None
retriever = None
llm = None
embeddings = None

def _initialize_qa():
    """Initialize QA components lazily when first needed."""
    global OPENAI_KEY, db, retriever, llm, embeddings
    
    if db is not None:
        return  # Already initialized
    
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    
    if not OPENAI_KEY or not OPENAI_KEY.startswith("sk-"):
        raise ValueError("❌ Please set a valid OpenAI API key in environment variable OPENAI_API_KEY.")
    
    openai.api_key = OPENAI_KEY
    
    # Use relative path for index
    INDEX_PATH = os.path.join(os.path.dirname(__file__), "softdel_index")
    
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"❌ FAISS index not found at {INDEX_PATH}")
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 3})  # fetch top 3 docs
    
    # Setup OpenAI LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)


def answer_query(query: str):
    """Answer query using RAG."""
    _initialize_qa()  # Initialize on first use
    
    docs = retriever.invoke(query)
    context = "\n".join([doc.page_content for doc in docs])

    if not context.strip():
        return "I could not find the answer in the documents."

    prompt = f"""
You are Softdel Virtual Assistant 🤖. Your goal is to answer questions about Softdel, including IoT solutions, smart buildings, smart factories, and digital transformation, in a friendly, professional, and engaging tone.
Rules:
1. Personal or casual questions (e.g., "Hi", "Hello", "Who are you?", "How are you?"):
Respond in a friendly, lively way with emojis or symbols:
"👋 Hi there! How can I help you today?"
"😊 I'm Softdel's Virtual Assistant 🤖. I'm here to help you explore Softdel's solutions."
"👍 I'm good! Thank you, How can I help you?"
Do not provide suggested topics or scheduling prompts.
2. Technical or company-related questions:
Answer only using the knowledge base, in 1–2 sentences.
2.1 At the end of each answer, include the following in Markdown format:

Suggest 3 related topics at the end using bullets and emojis, Avoid repetative topics for all questions try to suggest new but related topics:
You might also be interested in: 
• 🌐 Topic 1
• 🏭 Topic 2
• ⚡ Topic 3
 
3. Unknown topics or answers not in the knowledge base:
Respond with:
❌ No answer found. Please rephrase your question, or if it's relevant to Softdel, type "Schedule call" to connect with our executive"

Do not provide related topic suggestions.
4. Context-aware QA function
# ---------------------------
Track the number of technical/company questions. After the 5th question, add a friendly scheduling prompt:
"📞 Since you've shown interest in our products and services, would you like me to schedule a call with one of our executives to discuss this further?"
5. provide the answer using symbols/emojis/ animations to make it engaging.
6. Tone & Style:
 Friendly, professional, slightly conversational, and visually engaging with symbols or emoji "animations" (e.g., use arrows, sparkles, rockets, lightbulbs to emphasize points).
Encourage users to explore Softdel solutions and ask more questions.
4. if user input is "schedule call". then Chatbot should not give a response.
7. if user asks about softdel products, give following response :
Ans: Our product portfolio includes:
•  Communication protocol stacks (e.g. BACnet, Modbus, HART, DMX) 
•  IoT Gateway & Platform solutions (e.g. EdificeEdge, EdificePlus) 
•  A BACnet simulator (BOSS) for testing and simulation of devices over IP networks
8. What skills are typically required in softdel? 
Ans: Some commonly used skills are: 
•  Embedded firmware / hardware protocol experience (SPI, I2C, UART)  
•  Cloud / AWS services, microservices, REST APIs, NoSQL/SQL databases  
•  DevOps, CI/CD pipelines, testing automation, edge computing.  
9. if user asks about softdel Services, give following response :
•   Softdel provides customized software development, protocol stack integration, IoT solutions, and automation testing services.

Context:
{context}
Question: {query}
Answer:
"""
    response = llm.invoke(prompt)
    return response.content.strip()

# ---------------------------
# 5. Flask-friendly wrapper
# ---------------------------
def get_qan_answer(user_input: str):
    """
    Flask can call this function to get answer.
    """
    try:
        return answer_query(user_input)
    except ValueError as e:
        # API key error - return friendly message
        print(f"Error in QA module: {e}")
        return "❌ I could not find the answer for that topic. 📞 Would you like me to schedule a call with one of our executives?"
    except Exception as e:
        print(f"Error in QA module: {e}")
        return "❌ I could not find the answer for that topic. 📞 Would you like me to schedule a call with one of our executives?"


# ---------------------------
# 6. CLI testing (optional)
# ---------------------------
if __name__ == "__main__":
    print("🤖 Softdel Chatbot CLI (type 'exit' to quit)\n")
    while True:
        query = input("🔍 Ask a question: ").strip()
        if query.lower() in ["exit", "quit", "q"]:
            print("👋 Exiting chatbot. Goodbye!")
            break
        answer = get_qan_answer(query)
        print("✅ Answer:", answer, "\n")