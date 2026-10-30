
import ollama


class OllamaLLM:

    def __init__(self, model_name="qwen3.5:4b"):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            think=False,
            options={
                "temperature": 0.2,
                "num_predict": 256,
            }
        )

        return response.message.content
