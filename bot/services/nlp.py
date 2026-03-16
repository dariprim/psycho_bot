from typing import Tuple, List
import torch
from transformers import pipeline
from llama_cpp import Llama
from bot.config import MODEL_PATH, SENTIMENT_MODEL  
from bot.utils.helpers import detect_stress_type
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Путь к скачанному GGUF-файлу 
MODEL_PATH = os.getenv("MODEL_PATH")

class NLPProcessor:
    def __init__(self):
        # Загружаем GGUF-модель для генерации
        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,          # контекст (макс. длина диалога)
            n_threads=4,          # количество потоков CPU (можно увеличить)
            n_gpu_layers=0,       # 0 = только CPU
            verbose=False,
        )
        # Загружаем модель для анализа тональности (через transformers)
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_MODEL,
            tokenizer=SENTIMENT_MODEL,
            device=-1  # -1 = CPU
        )

    def generate_response(self, user_message: str, history: List[Tuple[str, str]] = None) -> str:
        """
        Генерирует ответ с учётом истории для модели YandexGPT.
        """

        # Замена символов новой строки на [NL] (как рекомендуется)
        user_message = user_message.replace('\n', ' [NL] ')

        # Формируем диалог в ожидаемом моделью формате
        dialogue = ""
        if history:
            for user, bot in history:
                # Обрабатываем каждое сообщение
                user_processed = user.replace('\n', ' [NL] ')
                bot_processed = bot.replace('\n', ' [NL] ')
                dialogue += f"{user_processed} Ассистент:[SEP] {bot_processed}</s>\n"

        # Добавляем текущее сообщение и сигнал для ответа модели
        dialogue += f"{user_message} Ассистент:[SEP]"

        # УЛУЧШЕННЫЙ СИСТЕМНЫЙ ПРОМПТ
        system_prompt = (
            "Ты — эмпатичный психолог. Твоя задача — поддержать человека, "
            "проявить понимание и дать мягкий совет, если уместно. "
            "Отвечай на русском языке простым текстом, без использования Markdown, "
            "звёздочек, жирного шрифта и других символов форматирования. "
            "Если приводишь список, используй обычные цифры с точкой (1., 2., ...). "
            "Старайся давать полные, законченные ответы.\n\n"
            "Важно: не предлагай обратиться к специалисту слишком навязчиво. "
            "Если пользователь говорит, что не хочет к специалисту, не настаивай. "
            "Вместо этого предложи конкретные техники самопомощи: дыхательные упражнения, "
            "методы релаксации, идеи для отвлечения, советы по изменению образа мыслей. "
            "Будь добрым, поддерживающим и практичным."
        )
        system_prompt_processed = system_prompt.replace('\n', ' [NL] ')
        
        # Собираем полный промпт: системная инструкция как первое сообщение пользователя, затем история, затем текущий запрос.
        full_prompt = f"{system_prompt_processed} Ассистент:[SEP] Понял, буду следовать инструкции.</s>\n{dialogue}"

        # Генерация через llama.cpp
        output = self.llm(
            full_prompt,
            max_tokens=400,          
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.15,
            stop=["</s>", "\nПользователь:"],  # останавливаемся на конце ответа или начале новой реплики
            echo=False
        )
        response = output["choices"][0]["text"].strip()

        response = response.replace('[NL]', '\n')
        response = '\n'.join(line.strip() for line in response.splitlines())
        
        return response

    def analyze_sentiment(self, text: str) -> str:
        result = self.sentiment_analyzer(text)[0]
        label = result['label'].lower()
        if 'positive' in label:
            return 'positive'
        elif 'negative' in label:
            return 'negative'
        return 'neutral'

    def classify_state(self, text: str) -> str:
        return detect_stress_type(text)

# Глобальный экземпляр 
nlp_processor = NLPProcessor()

def get_psychological_response(text: str, history=None) -> str:
    return nlp_processor.generate_response(text, history=history)

def analyze_sentiment(text: str) -> str:
    return nlp_processor.analyze_sentiment(text)

def classify_state(text: str) -> str:
    return nlp_processor.classify_state(text)