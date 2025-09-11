import os
import requests
import json
import logging
from abc import ABC, abstractmethod

from core.src.utils import load_ai_providers # Import the function to load provider data

from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    Defines the interface for AI operations.
    """
    def __init__(self, settings):
        self.settings = settings
        self.ai_model = settings.get("AI_MODEL") # This will be the general model for OpenAI/Gemini
        self.temperature = settings.get("AI_TEMPERATURE", 0.7)
        self.max_tokens = settings.get("AI_MAX_TOKENS", 150)
        self.local_endpoint = settings.get("LOCAL_AI_ENDPOINT") # For local models
        self.local_model_name = settings.get("LOCAL_AI_MODEL") # For local models

    @abstractmethod
    def summarize_chapter(self, chapter_title, chapter_text):
        """Generates a summary for a given chapter."""
        pass

    @abstractmethod
    def generate_social_post(self, chapter_title, chapter_text, tone, length):
        """Generates a social media post for a given chapter."""
        pass

    @abstractmethod
    def extract_characters(self, chapter_text):
        """Extracts character names from a chapter (to be implemented later)."""
        pass

class OpenAIProvider(AIProvider):
    """
    AI provider for OpenAI and Google Gemini models using LangChain.
    """
    def __init__(self, settings):
        super().__init__(settings)
        self.provider_name = settings.get("AI_PROVIDER")
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initializes the appropriate LangChain LLM based on the provider."""
        api_key = ""
        llm = None
        if self.provider_name.lower() == "openai":
            api_key = self.settings.get("OPENAI_API_KEY") or self.settings.get("AI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY or AI_API_KEY in your .env file.")
            llm = ChatOpenAI(
                openai_api_key=api_key,
                model_name=self.ai_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        elif self.provider_name.lower() == "google gemini":
            api_key = self.settings.get("GOOGLE_API_KEY") or self.settings.get("AI_API_KEY")
            if not api_key:
                raise ValueError("Google API key not found. Please set GOOGLE_API_KEY or AI_API_KEY in your .env file.")

            # Resolve the model name to its ID for Google Gemini
            providers_data = load_ai_providers()
            google_models = []
            for provider in providers_data.get("providers", []):
                if provider.get("name").lower() == "google gemini":
                    google_models = provider.get("models", [])
                    break
            
            model_id = None
            for model_entry in google_models:
                if model_entry.get("name") == self.ai_model: # Match by name, which is likely stored in .env
                    model_id = model_entry.get("id")
                    break
            
            if not model_id:
                raise ValueError(f"Google Gemini model '{self.ai_model}' not found or invalid in api_providers.json.")

            llm = ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=model_id, # Use the resolved model ID here
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Unsupported AI provider for OpenAIProvider: {self.provider_name}")
        return llm

    def summarize_chapter(self, chapter_title, chapter_text):
        summary_template = """You are a professional editor. Your task is to summarize a chapter from a book.
        Provide a concise summary of the chapter, 3-5 sentences long, highlighting key events, important character developments, and the overall tone.
        The summary should capture the essence of the chapter, suitable for a back-cover blurb or an internal review.

        Chapter Title: {chapter_title}

        Chapter Full Text:
        {text}

        CONCISE SUMMARY:"""

        summary_prompt = PromptTemplate(
            template=summary_template,
            input_variables=["chapter_title", "text"]
        )
        
        # We will use the stuff chain as we are passing the whole chapter text
        chain = load_summarize_chain(self.llm, chain_type="stuff", prompt=summary_prompt)
        docs = [Document(page_content=chapter_text)]
        summary_response = chain.invoke(
            {"input_documents": docs, "chapter_title": chapter_title},
            return_only_outputs=True
        )
        return summary_response["output_text"].strip()

    def generate_social_post(self, chapter_title, chapter_text, tone, length):
        template = """
        You are an expert social media manager. Your task is to draft a promotional social media post for a chapter of a book.
        
        Chapter Title: {chapter_title}
        Chapter Content: {chapter_text}
        
        Desired Tone: {tone}
        Desired Length: {length}
        
        Please draft a compelling social media post based on the chapter content, adhering to the specified tone and length. 
        Focus on engaging potential readers and highlighting key aspects or mysteries of the chapter without giving away major spoilers.
        Do not include hashtags or emojis unless explicitly asked for in the tone/length, just the post content itself.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["chapter_title", "chapter_text", "tone", "length"]
        )

        llm_chain = prompt | self.llm
        post_response = llm_chain.invoke({
            "chapter_title": chapter_title,
            "chapter_text": chapter_text,
            "tone": tone,
            "length": length
        })
        
        # Access the content attribute of the AIMessage object
        if isinstance(post_response, AIMessage):
            return post_response.content.strip()
        else:
            return str(post_response).strip() # Fallback for other response types

    def extract_characters(self, chapter_text):
        # To be implemented later
        logger.info("Character extraction not yet implemented for OpenAIProvider.")
        return []

class LocalLLMProvider(AIProvider):
    """
    AI provider for local LLMs (Ollama, LM Studio, TextGen WebUI) via a common API endpoint.
    Assumes an OpenAI-compatible API endpoint.
    """
    def __init__(self, settings):
        super().__init__(settings)
        if not self.local_endpoint:
            raise ValueError("Local AI endpoint not configured. Please set LOCAL_AI_ENDPOINT in your .env file.")
        if not self.local_model_name:
            raise ValueError("Local AI model not configured. Please set LOCAL_AI_MODEL in your .env file.")
        
        # Ensure endpoint ends with /v1 if it's not already for OpenAI compatible API
        if not self.local_endpoint.endswith("/v1"):
            self.api_base = f"{self.local_endpoint.rstrip('/')}/v1"
        else:
            self.api_base = self.local_endpoint.rstrip('/') # Should be /v1 already


    def _call_local_llm(self, messages, max_tokens=None):
        """Helper to send a request to the local LLM endpoint."""
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.local_model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens if max_tokens else self.max_tokens,
            "stream": False # For now, we don't handle streaming
        }
        
        try:
            # For local models, API key might not be required, but some setups might use a dummy one.
            # We will not send an API key by default here.
            response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=payload, timeout=300)
            response.raise_for_status() # Raise an exception for HTTP errors
            
            result = response.json()
            if result and result.get("choices") and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"Local LLM response did not contain expected content: {result}")
                return "Error: Unexpected response format from local LLM."
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling local LLM at {self.api_base}: {e}")
            raise ConnectionError(f"Failed to connect to local LLM: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from local LLM: {e}")
            raise ValueError(f"Invalid JSON response from local LLM: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during local LLM call: {e}")
            raise

    def summarize_chapter(self, chapter_title, chapter_text):
        messages = [
            {"role": "system", "content": "You are a professional editor. Your task is to summarize a chapter from a book."},
            {"role": "user", "content": f"""Provide a concise summary of the chapter, 3-5 sentences long, highlighting key events, important character developments, and the overall tone.
The summary should capture the essence of the chapter, suitable for a back-cover blurb or an internal review.

Chapter Title: {chapter_title}

Chapter Full Text:
{chapter_text}

CONCISE SUMMARY:"""}
        ]
        return self._call_local_llm(messages)

    def generate_social_post(self, chapter_title, chapter_text, tone, length):
        messages = [
            {"role": "system", "content": "You are an expert social media manager. Your task is to draft a promotional social media post for a chapter of a book."},
            {"role": "user", "content": f"""Draft a compelling social media post based on the chapter content, adhering to the specified tone and length. 
Focus on engaging potential readers and highlighting key aspects or mysteries of the chapter without giving away major spoilers.
Do not include hashtags or emojis unless explicitly asked for in the tone/length, just the post content itself.

Chapter Title: {chapter_title}
Chapter Content: {chapter_text}

Desired Tone: {tone}
Desired Length: {length}
"""}
        ]
        return self._call_local_llm(messages)

    def extract_characters(self, chapter_text):
        # To be implemented later for local LLMs
        logger.info("Character extraction not yet implemented for LocalLLMProvider.")
        return []
