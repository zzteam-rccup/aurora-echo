from pydantic import BaseModel
from kernel.availability import check_availability
from kernel.analysis.chatgpt import ChatGPT
from kernel.analysis.claude import Claude
from kernel.analysis.llama import Llama
from kernel.analysis.qwen import Qwen
from kernel.analysis.mistral_ai import MistralAI
from kernel.analysis.utils import StructureSchema

availability = check_availability()
if not availability:
    print(
        'WARN: The official OpenAI service is not in your country. You can not access to the Structured Output & '
        'Database Query features.'
    )


class GeneratePromptConfig(BaseModel):
    expression: str
    feedback: str
    product_desc: str


class LargeLanguageModel:
    def __init__(self):
        self.model = None
        self.overall = open('static/openai/overall.txt', 'r').read()
        self.object = open('static/openai/object.txt', 'r').read()
        self.subject = open('static/openai/subject.txt', 'r').read()
        self.json = open('static/openai/json.txt', 'r').read()

    def generate_prompt(self, target, config: GeneratePromptConfig, single: bool):
        if target != 'object' and target != 'subject' and target != 'json':
            raise ValueError('target must be either "object", "subject", or "json"')

        overall_prompt = (self.overall.replace(
            '{{ expression }}', config.expression
        ).replace(
            '{{ product_desc }}', str(config.product_desc)
        ))
        user_prompt = self.object if target == 'object' else self.subject if target == 'subject' else self.json
        user_prompt = user_prompt.replace('{{ feedback }}', config.feedback)

        prompt = [
            {"role": "system", "content": overall_prompt},
            {"role": "user", "content": user_prompt}
        ] if single else [{"role": "user", 'content': f"{overall_prompt}\n\n{user_prompt}"}]

        return prompt

    def switch(self, model):
        self.model = model

    def __call__(self, target, config: GeneratePromptConfig):
        prompt = self.generate_prompt(target, config, single=self.model == 'claude')
        if target == 'json' and availability:
            # Only official OpenAI API (2024-08-06) supports the structured output feature.
            return ChatGPT('openai').json(prompt, schema=StructureSchema)
        elif self.model == 'chatgpt':
            return ChatGPT('openai' if availability else 'burn-hair').message(prompt)
        elif self.model == 'deepseek':
            return ChatGPT('deepseek').message(prompt)
        elif self.model == 'burn-hair':
            return ChatGPT('burn-hair').message(prompt)
        elif self.model == 'claude' and availability:
            return Claude().message(prompt)
        elif self.model == 'llama':
            return Llama().message(prompt)
        elif self.model == 'qwen':
            return Qwen().message(prompt)
        elif self.model == 'mistral' and availability:
            return MistralAI().message(prompt)
        else:
            raise ValueError('model must be either "chatgpt", "claude", "llama", "qwen", or "mistral"')
