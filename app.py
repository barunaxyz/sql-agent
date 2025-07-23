import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.graph import app
from graph.state import ChatState

st.set_page_config(page_title="SQL Chatbot", page_icon="📊")

st.title("Chatbot Agent")
st.markdown("Tanyakan pertanyaan terkait database kamu!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

user_input = st.chat_input("Tulis pertanyaan kamu...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    state: ChatState = {
        "messages": st.session_state.messages,
        "user_input": user_input,
        "answer": None
    }

    result = app.invoke(state)

    st.session_state.messages = result["messages"]

    with st.chat_message("assistant"):
        st.markdown(result["answer"])
