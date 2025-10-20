"""
Local LLM client for connecting to various local LLM APIs
"""

import os
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LocalLLMClient:
    """Client for connecting to local LLM APIs"""
    
    def __init__(self):
        self.api_endpoint = os.getenv('GPT_API', 'http://localhost:11434/v1/chat/completions')
        self.api_key = os.getenv('API_KEY', '')
        self.model_name = os.getenv('MODEL_NAME', 'llama2')
        
        # Validate configuration
        if not self.api_endpoint:
            raise ValueError("GPT_API environment variable not set")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        return headers
    
    def generate_summary(self, recipe_text: str) -> Optional[str]:
        """
        Generate a summary of the given recipe using the local LLM
        
        Args:
            recipe_text: The formatted recipe text to summarize
            
        Returns:
            Summary text or None if generation fails
        """
        prompt = f"""Please provide a concise summary of this recipe in 2-3 sentences. Focus on the main dish, key ingredients, and cooking method:

{recipe_text}

Summary:"""
        
        try:
            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            # Make the API request
            response = requests.post(
                self.api_endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Try to extract the response text from different possible formats
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', '')
                    return content.strip()
                elif 'response' in result:
                    # Some local APIs use 'response' instead of 'choices'
                    return result['response'].strip()
                else:
                    print(f"Unexpected response format: {result}")
                    return None
            else:
                print(f"API request failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to LLM API: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in LLM generation: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test the connection to the local LLM API
        
        Returns:
            True if connection is successful, False otherwise
        """
        test_prompt = "Hello, please respond with 'Connection successful!'"
        
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": test_prompt
                    }
                ],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            response = requests.post(
                self.api_endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status information about the LLM client"""
        return {
            "api_endpoint": self.api_endpoint,
            "model_name": self.model_name,
            "has_api_key": bool(self.api_key),
            "connection_ok": self.test_connection()
        }