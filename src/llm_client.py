"""
Local LLM Client for Qwen Integration

This module provides functionality to interact with local Qwen LLM via Ollama API.
Supports streaming responses and chat history management.
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


class OllamaAPIError(Exception):
    """Custom exception for Ollama API errors."""
    pass


class LLMClient:
    """Client for interacting with local LLM via LM Studio API."""
    
    def __init__(self, base_url: str = "http://localhost:1234", model: str = "qwen2.5:latest"):
        """
        Initialize the LLM client.
        
        Args:
            base_url: Base URL for LM Studio API
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "arxiv-rag-pipeline/1.0"
        })
    
    def check_connection(self) -> bool:
        """
        Check if LM Studio API is accessible.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Check if LM Studio is running
            response = self.session.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code != 200:
                return False
            
            # LM Studio should return a list of models
            models = response.json().get("data", [])
            return len(models) > 0
            
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False
    
    def generate_response(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated response text
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise OllamaAPIError(f"API request failed: {response.status_code} - {response.text}")
            
            if stream:
                return self._parse_streaming_response(response)
            else:
                return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                
        except requests.exceptions.RequestException as e:
            raise OllamaAPIError(f"Request failed: {e}")
    
    def generate_streaming_response(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response from the LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks as they arrive
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                raise OllamaAPIError(f"API request failed: {response.status_code} - {response.text}")
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                        if data.get('choices', [{}])[0].get('finish_reason'):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            raise OllamaAPIError(f"Request failed: {e}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        Generate a chat completion from a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated response text
        """
        # Convert messages to a single prompt for Ollama
        prompt = self._format_messages_as_prompt(messages)
        return self.generate_response(prompt, temperature, max_tokens, stream)
    
    def chat_completion_streaming(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Generator[str, None, None]:
        """
        Generate a streaming chat completion from a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks as they arrive
        """
        prompt = self._format_messages_as_prompt(messages)
        yield from self.generate_streaming_response(prompt, temperature, max_tokens)
    
    def _format_messages_as_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Format a list of messages into a single prompt for Ollama.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts) + "\n\nAssistant:"
    
    def _parse_streaming_response(self, response) -> str:
        """
        Parse a streaming response and return the complete text.
        
        Args:
            response: Streaming response object
            
        Returns:
            Complete response text
        """
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if 'response' in data:
                        full_response += data['response']
                    if data.get('done', False):
                        break
                except json.JSONDecodeError:
                    continue
        
        return full_response
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model.get("name") == self.model:
                        return {
                            "name": model.get("name"),
                            "size": model.get("size"),
                            "modified_at": model.get("modified_at"),
                            "digest": model.get("digest")
                        }
            return {"name": self.model, "status": "unknown"}
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"name": self.model, "status": "error", "error": str(e)}


def create_llm_client(config: Dict[str, Any]) -> LLMClient:
    """
    Create an LLM client from configuration.
    
    Args:
        config: Configuration dictionary with LLM settings
        
    Returns:
        Configured LLMClient instance
    """
    llm_config = config.get("llm", {})
    base_url = llm_config.get("base_url", "http://localhost:11434")
    model = llm_config.get("model", "qwen2.5:latest")
    
    return LLMClient(base_url=base_url, model=model)


def test_llm_connection() -> bool:
    """
    Test LLM connection and return status.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        client = LLMClient()
        return client.check_connection()
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        return False


def main():
    """Test the LLM client."""
    client = LLMClient()
    
    print(f"Testing connection to Ollama at {client.base_url}")
    if client.check_connection():
        print("✅ Connection successful!")
        
        # Test basic generation
        print("\nTesting basic generation...")
        response = client.generate_response("Hello, how are you?")
        print(f"Response: {response}")
        
        # Test chat completion
        print("\nTesting chat completion...")
        messages = [
            {"role": "user", "content": "What is machine learning?"}
        ]
        response = client.chat_completion(messages)
        print(f"Chat response: {response}")
        
    else:
        print("❌ Connection failed!")
        print("Make sure Ollama is running and the model is available.")


if __name__ == "__main__":
    main()
