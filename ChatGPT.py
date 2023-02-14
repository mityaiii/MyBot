from Config import Config
import openai


class ChatGPT:
    openai.api_key = Config.config["CHATGPT"]["key"]
    phrases_for_ignore = ["Выбрать предмет", "Помощь"]

    def get_answer(msg: str) -> str:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=msg,
            temperature=0.5,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )
        return response["choices"][0]['text']
