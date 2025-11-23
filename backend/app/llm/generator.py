"""
LLM generator for RAG responses.
Uses Ollama for local LLM inference.
"""

import requests
import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LLMGenerator:
    """Generate responses using a local LLM via Ollama."""
    
    def __init__(
        self,
        model_name: str = "mistral",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        """
        Initialize the LLM generator.
        
        Args:
            model_name: Name of the Ollama model
            base_url: Ollama API base URL
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"LLMGenerator initialized with model: {model_name}")
    
    def check_model_available(self) -> bool:
        """
        Check if the model is available in Ollama.
        
        Returns:
            True if model is available
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'].startswith(self.model_name) for model in models)
            return False
        except Exception as e:
            logger.error(f"Error checking model availability: {str(e)}")
            return False
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text
        """
        try:
            # Prepare request
            logger.info(f"Sending prompt to LLM (length {len(prompt)}): {prompt[:200]}...")
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                # "options": {
                #     "temperature": temperature or self.temperature,
                #     "num_predict": max_tokens or self.max_tokens
                # }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            # Make request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                logger.info(f"LLM Response length: {len(generated_text)}")
                if not generated_text:
                    logger.warning(f"LLM returned empty response. Raw result: {result}")
                return generated_text
            else:
                logger.error(f"LLM generation failed with status {response.status_code}: {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return ""
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate chat response using the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens
                }
            }
            
            logger.info(f"Sending chat request to LLM with {len(messages)} messages")
            # logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            with open("last_payload.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('message', {})
                return message.get('content', '').strip()
            else:
                logger.error(f"LLM chat failed with status {response.status_code}: {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating LLM chat response: {str(e)}")
            return ""

    def generate_rag_response(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        max_context_length: int = 2000
    ) -> str:
        """
        Generate a RAG response with retrieved context.
        
        Args:
            query: User query
            context_documents: Retrieved documents with metadata
            max_context_length: Maximum context length in characters
            
        Returns:
            Generated answer
        """
        # Build context from retrieved documents
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(context_documents, 1):
            doc_text = doc.get('document', '')
            metadata = doc.get('metadata', {})
            
            # Format context with source info
            source_info = f"Source {i}"
            if 'filename' in metadata:
                source_info += f" ({metadata['filename']}"
                if 'page_number' in metadata:
                    source_info += f", Page {metadata['page_number']}"
                if 'timestamp' in metadata:
                    source_info += f", {metadata['timestamp']}"
                source_info += ")"
            
            context_part = f"[{source_info}]\n{doc_text}\n"
            
            # Check if adding this would exceed max length
            if current_length + len(context_part) > max_context_length:
                break
            
            context_parts.append(context_part)
            current_length += len(context_part)
        
        context = "\n".join(context_parts)
        
        # Create system message
        system_message = (
            "You are a knowledgeable AI assistant specializing in analyzing documents. "
            "Your goal is to provide accurate, comprehensive answers based ONLY on the provided context. "
            "Always cite your sources using the format [Source X] at the end of sentences where information is used. "
            "If the context is insufficient, clearly state what is missing."
        )
        
        # Create user message with context
        user_content = f"""Context information is below:
---------------------
{context}
---------------------

Using the context above, answer this question: {query}"""

        messages = [
            # {"role": "system", "content": system_message},
            {"role": "user", "content": system_message + "\n\n" + user_content}
        ]
        
        response = self.chat(messages)
        
        return response
    
    def summarize_document(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of a document.
        
        Args:
            text: Document text
            max_length: Maximum summary length in words
            
        Returns:
            Summary text
        """
        prompt = f"""Please provide a concise summary of the following text in no more than {max_length} words:

{text[:3000]}  # Limit input text length

Summary:"""
        
        system_prompt = "You are a helpful assistant that creates concise and accurate summaries."
        
        return self.generate(prompt=prompt, system_prompt=system_prompt)
    
    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """
        Extract key points from text.
        
        Args:
            text: Document text
            num_points: Number of key points to extract
            
        Returns:
            List of key points
        """
        prompt = f"""Please extract the {num_points} most important key points from the following text. 
List them as numbered points.

{text[:3000]}

Key points:"""
        
        response = self.generate(prompt=prompt)
        
        # Parse numbered points
        lines = response.split('\n')
        points = [line.strip() for line in lines if line.strip() and any(c.isdigit() for c in line[:3])]
        
        return points[:num_points]
