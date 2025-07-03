from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

load_dotenv()

openai_client = OpenAI()
openai_async_client = AsyncOpenAI()

class LLMFetcher:
    def __init__(self, provider, model = 'gpt-4.1-mini'):
        self.model = model
        self._set_client(provider)

    def _set_client(self, provider):
        if (provider == 'openai'):
            self.client = openai_client
            self.async_client = openai_async_client
        else:
            raise Exception(detail = 'You must pass \'openai\' as a provider.')
