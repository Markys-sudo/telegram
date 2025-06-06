from config import PROXY_GPT
from openai import AsyncOpenAI
import httpx
import base64
import mimetypes



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
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.message_list,
            max_tokens=3000,
            temperature=0.9
        )
        message = response.choices[0].message
        # self.message_list.append(message)
        return message.content

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        reply = await self.send_message_list()
        self.message_list.append({"role": "assistant", "content": reply})
        return reply

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list = [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": message_text}
        ]
        return await self.send_message_list()

    async def describe_image(self, file_path: str, prompt: str = "Опиши, що зображено на цьому фото українською мовою.") -> str:
        # Визначаємо MIME-тип (важливо для правильного формату запиту)
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "image/jpeg"

        # Читаємо і кодуємо зображення у base64
        with open(file_path, "rb") as img_file:
            b64_data = base64.b64encode(img_file.read()).decode("utf-8")

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_data}"}}
                ]}
            ],
            max_tokens=800,
        )

        return response.choices[0].message.content