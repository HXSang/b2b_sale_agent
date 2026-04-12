# import os
# from dotenv import load_dotenv

# load_dotenv()

# class ConfigManager:
#     def __init__(self):
#         self.api_key = os.getenv("GROK_API_KEY")
#         self.base_url = os.getenv("LLM_BASE_URL")
#         self.primary_model = os.getenv("LLM_MODEL_PRIMARY")
        
#         self._validate_config()
        
#     def _validate_config(self):
#         missing_keys = []
#         if not self.api_key: missing_keys.append("GROK_API_KEY")
#         if not self.base_url: missing_keys.append("LLM_BASE_URL")
#         if not self.primary_model: missing_keys.append("LLM_MODEL_PRIMARY")
        
#         if missing_keys:
#             raise ValueError(f"Error System. Missing value: {', '.join(missing_keys)} in file .env")
        
# config = ConfigManager()