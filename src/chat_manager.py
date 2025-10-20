"""
Chat Session Management

This module provides functionality to manage chat sessions, save/load chat history,
and handle conversation persistence for the RAG pipeline.
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# Set up logging
logger = logging.getLogger(__name__)


class ChatSession:
    """Represents a chat session with history and metadata."""
    
    def __init__(self, session_id: str = None, topic: str = None):
        """
        Initialize a chat session.
        
        Args:
            session_id: Unique session identifier
            topic: Research topic for this session
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.topic = topic
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.messages: List[Dict[str, Any]] = []
    
    def add_message(
        self, 
        role: str, 
        content: str, 
        retrieved_context: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add a message to the session.
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            retrieved_context: Optional RAG context used for this message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "retrieved_context": retrieved_context or []
        }
        
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_recent_messages(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Get the most recent messages from the session.
        
        Args:
            count: Number of recent messages to return
            
        Returns:
            List of recent message dictionaries
        """
        return self.messages[-count:] if self.messages else []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history in format suitable for LLM.
        
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create session from dictionary."""
        session = cls(
            session_id=data.get("session_id"),
            topic=data.get("topic")
        )
        session.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        session.updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        session.messages = data.get("messages", [])
        return session


class ChatManager:
    """Manages chat sessions and persistence."""
    
    def __init__(self, save_dir: str = "./chat_history", auto_save: bool = True):
        """
        Initialize the chat manager.
        
        Args:
            save_dir: Directory to save chat sessions
            auto_save: Whether to automatically save sessions
        """
        self.save_dir = Path(save_dir)
        self.auto_save = auto_save
        self.current_session: Optional[ChatSession] = None
        
        # Ensure save directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def start_new_session(self, topic: str = None) -> ChatSession:
        """
        Start a new chat session.
        
        Args:
            topic: Research topic for this session
            
        Returns:
            New chat session
        """
        self.current_session = ChatSession(topic=topic)
        logger.info(f"Started new chat session: {self.current_session.session_id}")
        return self.current_session
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Load an existing chat session.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            Loaded session or None if not found
        """
        session_file = self.save_dir / f"{session_id}.json"
        
        if not session_file.exists():
            logger.warning(f"Session file not found: {session_file}")
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = ChatSession.from_dict(data)
            self.current_session = session
            logger.info(f"Loaded chat session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def save_session(self, session: ChatSession = None) -> bool:
        """
        Save a chat session to disk.
        
        Args:
            session: Session to save (uses current session if None)
            
        Returns:
            True if successful, False otherwise
        """
        if session is None:
            session = self.current_session
        
        if session is None:
            logger.warning("No session to save")
            return False
        
        try:
            session_file = self.save_dir / f"{session.session_id}.json"
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved chat session: {session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")
            return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available chat sessions.
        
        Returns:
            List of session metadata dictionaries
        """
        sessions = []
        
        for session_file in self.save_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sessions.append({
                    "session_id": data.get("session_id"),
                    "topic": data.get("topic"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "message_count": len(data.get("messages", []))
                })
                
            except Exception as e:
                logger.error(f"Failed to read session file {session_file}: {e}")
        
        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        session_file = self.save_dir / f"{session_id}.json"
        
        if not session_file.exists():
            logger.warning(f"Session file not found: {session_file}")
            return False
        
        try:
            session_file.unlink()
            logger.info(f"Deleted chat session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def add_message(
        self, 
        role: str, 
        content: str, 
        retrieved_context: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add a message to the current session.
        
        Args:
            role: Message role
            content: Message content
            retrieved_context: Optional RAG context
        """
        if self.current_session is None:
            logger.warning("No active session, creating new one")
            self.start_new_session()
        
        self.current_session.add_message(role, content, retrieved_context)
        
        if self.auto_save:
            self.save_session()
    
    def get_current_session(self) -> Optional[ChatSession]:
        """Get the current active session."""
        return self.current_session
    
    def get_session_summary(self, session: ChatSession = None) -> Dict[str, Any]:
        """
        Get a summary of a chat session.
        
        Args:
            session: Session to summarize (uses current session if None)
            
        Returns:
            Session summary dictionary
        """
        if session is None:
            session = self.current_session
        
        if session is None:
            return {"error": "No active session"}
        
        user_messages = [msg for msg in session.messages if msg["role"] == "user"]
        assistant_messages = [msg for msg in session.messages if msg["role"] == "assistant"]
        
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "total_messages": len(session.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "last_message": session.messages[-1] if session.messages else None
        }


def create_chat_manager(config: Dict[str, Any]) -> ChatManager:
    """
    Create a chat manager from configuration.
    
    Args:
        config: Configuration dictionary with chat history settings
        
    Returns:
        Configured ChatManager instance
    """
    chat_config = config.get("chat_history", {})
    save_dir = chat_config.get("save_dir", "./chat_history")
    auto_save = chat_config.get("auto_save", True)
    
    return ChatManager(save_dir=save_dir, auto_save=auto_save)


def main():
    """Test the chat manager."""
    manager = ChatManager()
    
    # Test creating a new session
    print("Creating new session...")
    session = manager.start_new_session("machine learning")
    print(f"Session ID: {session.session_id}")
    
    # Test adding messages
    print("\nAdding messages...")
    manager.add_message("user", "What is machine learning?")
    manager.add_message("assistant", "Machine learning is a subset of artificial intelligence...")
    
    # Test saving
    print("\nSaving session...")
    success = manager.save_session()
    print(f"Save successful: {success}")
    
    # Test listing sessions
    print("\nListing sessions...")
    sessions = manager.list_sessions()
    for session_info in sessions:
        print(f"Session: {session_info['session_id']} - {session_info['topic']}")
    
    # Test loading session
    if sessions:
        print(f"\nLoading session: {sessions[0]['session_id']}")
        loaded_session = manager.load_session(sessions[0]['session_id'])
        if loaded_session:
            print(f"Loaded session with {len(loaded_session.messages)} messages")
    
    # Test session summary
    print("\nSession summary:")
    summary = manager.get_session_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
