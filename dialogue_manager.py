"""
DialogueManager for the Wellness Bot - Simple wrapper around wellness_bot
"""
from wellness_bot import initialize_bot
import requests

class DialogueManager:
    """
    Simple wrapper around the wellness_bot's reply function with conversation saving
    """
    
    def __init__(self, save_conversations=True, api_base_url="http://127.0.0.1:5000"):
        """
        Initialize DialogueManager
        
        Args:
            save_conversations (bool): Whether to save conversations to database
            api_base_url (str): Base URL for API calls
        """
        self.save_conversations = save_conversations
        self.api_base_url = api_base_url
        # Initialize the wellness bot instance for language persistence
        self.wellness_bot = initialize_bot()
        
    def handle_input(self, user_message, session_id="default", username=None):
        """
        Handle user input and return bot response
        
        Args:
            user_message (str): User's input message
            session_id (str): Session identifier for context
            username (str): Username for saving conversations
            
        Returns:
            str: Bot's response
        """
        if not user_message or not user_message.strip():
            return "I didn't receive any message. Could you please say something?"
        
        try:
            # Use the wellness_bot instance's reply method which handles all the dialogue logic
            response = self.wellness_bot.reply(user_message.strip(), session_id)
            
            # Save conversation if enabled and username provided
            if self.save_conversations and username:
                self._save_conversation(username, user_message.strip(), response)
            
            return response
        except Exception as e:
            return "Sorry, I encountered an unexpected error. Please try again."
    
    def _save_conversation(self, username, user_message, bot_response):
        """
        Save conversation to database via API
        
        Args:
            username (str): Username
            user_message (str): User's message
            bot_response (str): Bot's response
        """
        try:
            requests.post(
                f"{self.api_base_url}/save_conversation",
                json={
                    "username": username,
                    "user_message": user_message,
                    "bot_response": bot_response
                },
                timeout=5
            )
        except Exception as e:
            print(f"Failed to save conversation: {e}")
    
    def get_user_conversations(self, username, limit=50):
        """
        Get user's conversation history via API
        
        Args:
            username (str): Username
            limit (int): Maximum number of conversations to retrieve
            
        Returns:
            list: List of conversation dictionaries
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/get_conversations",
                params={"username": username, "limit": limit},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("conversations", [])
            
            return []
        except Exception as e:
            print(f"Failed to get conversations: {e}")
            return []
    
    def clear_user_conversations(self, username):
        """
        Clear all conversations for a user via API
        
        Args:
            username (str): Username
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/clear_conversations",
                json={"username": username},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            
            return False
        except Exception as e:
            print(f"Failed to clear conversations: {e}")
            return False
    
    def get_greeting(self, session_id="default"):
        """Get a greeting message for new chat sessions"""
        # Use the wellness_bot instance to get language-aware greeting
        return self.wellness_bot.reply("Hello", session_id)
    
    def get_help_message(self):
        """Get help message explaining bot capabilities"""
        return """I can help you with:
        
🏥 **Health Symptoms**: Tell me about headaches, fever, cough, dizziness, etc.
💡 **Medical Advice**: Get general guidance for common health issues
❓ **Health Questions**: Ask about symptom duration, severity, or treatment
🗣️ **Natural Conversation**: Just talk to me normally!

Try saying things like:
- "I have a headache"
- "How long does a fever last?"
- "I feel dizzy, what should I do?"

⚠️ **Important**: I provide general information only. For serious symptoms or emergencies, please consult a healthcare professional immediately."""
