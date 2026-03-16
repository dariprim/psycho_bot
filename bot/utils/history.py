from collections import defaultdict, deque
from typing import Dict, Deque, List, Tuple

class DialogHistory:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.history: Dict[int, Deque[Tuple[str, str]]] = defaultdict(lambda: deque(maxlen=max_messages))

    def add_message(self, user_id: int, user_text: str, bot_text: str):
        """Добавляет пару (сообщение пользователя, ответ бота) в историю."""
        self.history[user_id].append((user_text, bot_text))

    def get_history(self, user_id: int) -> List[Tuple[str, str]]:
        """Возвращает историю для пользователя в виде списка (user, bot)."""
        return list(self.history[user_id])

    def clear_history(self, user_id: int):
        """Очищает историю пользователя."""
        if user_id in self.history:
            del self.history[user_id]

# Глобальный экземпляр (для простоты)
dialog_history = DialogHistory()