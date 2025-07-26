
import streamlit as st
import requests
from embedder import collection

def generate_rag_response(query):
    # Query ChromaDB for relevant context
    results = collection.query(query_texts=[query], n_results=3)
    top_6_docs = results['documents'][0]
    context = "\n".join(top_6_docs)
    
    # Include chat history for short-term memory
    prompt = f"""Answer the following question according to the given context precisely.

        Context from knowledge base:
        {context}


        প্রশ্ন: {query}
        উত্তর:"""
    print(prompt)
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature":0.5,
                "top_p":0.7,  
            }
        }
    )
    
    return response.json()["response"]

# Streamlit UI
st.set_page_config(page_title="RAG Chat Bot", page_icon="🤖")
st.title("🤖 RAG Chat Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "আসসালামু আলাইকুম! আমি আপনার প্রশ্নের উত্তর দিতে প্রস্তুত।"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("আপনার প্রশ্ন লিখুন..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("উত্তর খোঁজা হচ্ছে..."):
            # Create chat history context (last 4 exchanges)
            recent_history = ""
            if len(st.session_state.messages) > 1:
                recent_messages = st.session_state.messages[-8:]  # Last 4 exchanges
                recent_history = "\n".join([
                    f"{'ব্যবহারকারী' if msg['role'] == 'user' else 'সহায়ক'}: {msg['content']}"
                    for msg in recent_messages
                ])

            response = generate_rag_response(prompt)
            st.write(response)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with info
with st.sidebar:
    st.header("📊 Chat Info")
    st.write(f"**Total Messages:** {len(st.session_state.messages)}")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "আসসালামু আলাইকুম! আমি আপনার প্রশ্নের উত্তর দিতে প্রস্তুত।"}
        ]
        st.rerun()
