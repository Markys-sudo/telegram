from config import PROXY_GPT
from openai import AsyncOpenAI
import httpx


class ChatGptService:
    def __init__(self, token: str):
        token = "sk-proj-" + token[:3:-1] if token.startswith('gpt:') else token
        self.client = AsyncOpenAI(
            http_client=httpx.AsyncClient(proxy=PROXY_GPT),
            api_key=token
        )

        self.message_list = []

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def send_message_list(self) -> str:
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.message_list,
            max_tokens=3000,
            temperature=0.9
        )
        message = completion.choices[0].message
        self.message_list.append(message)
        return message.content

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list = [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": message_text}
        ]
        return await self.send_message_list()
