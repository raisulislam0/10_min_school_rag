
import streamlit as st
import requests
from embedder import collection

def generate_rag_response(query, chat_history="", min_similarity_score=0.4):
    # Query ChromaDB for relevant context with distances
    results = collection.query(
        query_texts=[query], 
        n_results=6,
        include=["documents", "distances"]
    )
    
    documents = results['documents'][0]
    distances = results['distances'][0]
    
    # Filter documents by similarity score (lower distance = higher similarity)
    # Convert distance to similarity: similarity = 1 - distance
    filtered_docs = []
    for doc, distance in zip(documents, distances):
        similarity = 1 - distance
        if similarity >= min_similarity_score:
            filtered_docs.append(doc)
    
    # Use filtered context or empty if no relevant docs
    context = "\n".join(filtered_docs) if filtered_docs else ""
    
    if not context:
        return "দুঃখিত, আপনার প্রশ্নের জন্য পর্যাপ্ত প্রাসঙ্গিক তথ্য পাওয়া যায়নি।"
    
    prompt = f"""Answer the following question according to the given context precisely.

        Context from knowledge base:
        {context}

        {f"Previous conversation:{chat_history}" if chat_history else ""}

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
                "temperature":0.7,
                "top_p":0.95,  
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

            response = generate_rag_response(prompt, recent_history, min_similarity_score=0.4)
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
