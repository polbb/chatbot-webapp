"""Simple Streamlit web app for interacting with the SuperFi chatbot API."""
import streamlit as st
import requests
from uuid import UUID
from datetime import datetime
from typing import Optional

class ChatInterface:
    """Interface for communicating with the chatbot API."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """Initialize the chat interface."""
        self.api_url = api_url
        self.session_id: Optional[UUID] = None
    
    def send_message(self, message: str) -> dict:
        """Send a message to the chatbot API."""
        endpoint = f"{self.api_url}/chat"
        
        payload = {
            "question": message,
            "session_id": str(self.session_id) if self.session_id else None
        }
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Update session ID if this is first message
        if not self.session_id:
            self.session_id = UUID(data["session_id"])
        
        return data
    
    def get_history(self) -> list:
        """Get chat history from the API."""
        if not self.session_id:
            return []
            
        endpoint = f"{self.api_url}/chat/history/{self.session_id}"
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()["messages"]

def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="SuperFi Chat",
        page_icon="💬",
        layout="centered"
    )
    
    st.title("SuperFi Chat")
    
    # Initialize chat interface
    if "chat_interface" not in st.session_state:
        st.session_state.chat_interface = ChatInterface()
    
    # Initialize messages list
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Chat input
    with st.container():
        message = st.chat_input("Type your message here...")
        
        if message:
            try:
                # Send message to API
                response = st.session_state.chat_interface.send_message(message)
                
                # Add to message history
                st.session_state.messages.append({
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.now().isoformat()
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "timestamp": datetime.now().isoformat(),
                    "sources": response["sources"]
                })
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])
                if msg.get("sources"):
                    st.caption(f"Sources: {', '.join(msg['sources'])}")

if __name__ == "__main__":
    main() 