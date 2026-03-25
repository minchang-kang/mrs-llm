
import os
import backoff
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()
api_key = os.getenv("GPT_KEY")

class LLM:
    def __init__(self, provider: str, model: str, **kwargs):
        self.provider = provider
        self.model = model
        self.chat = kwargs['chat']
        self.debug = kwargs['debug']
        self.usage = None
        self.total_cost = 0
        self.client = OpenAI(api_key=api_key)

        if self.chat:
            self.sampling_params = {
                "max_tokens": kwargs['max_tokens'],
                "temperature": kwargs['temperature'],
            }

    @backoff.on_exception(backoff.expo, OpenAIError)
    def generate(self, prompt, conversation_id=None, previous_response_id=None):
        if self.provider == 'openai':
            try:
                if self.chat:
                    response = self.client.responses.create(
                        instructions="You are a helper assistant.",
                        model= self.model,
                        prompt=prompt,
                        conversation=conversation_id,
                        previous_response_id=previous_response_id,
                        **self.sampling_params
                    )
                    self.usage = response.usage
                    if self.debug:
                        ## debugging 함수
                        pass

                generated_samples = [response.output_text]

            except OpenAIError as e:
                print(f"In LLM class\nError:{e}")
        else:
            pass

        self.calculate_cost()
        return generated_samples, response.id
    
    def calculate_cost(self):
        if 'gpt-4-0125-preview' in self.model:
            usage = self.usage.prompt_tokens * 0.01 / 1000 + self.usage.completion_tokens * 0.03 / 1000
        elif 'gpt-3.5-turbo-1106' in self.model:
            usage = self.usage.prompt_tokens * 0.0015 / 1000 + self.usage.completion_tokens * 0.002 / 1000 

        self.total_cost += usage