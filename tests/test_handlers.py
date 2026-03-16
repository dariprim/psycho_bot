import pytest
from unittest.mock import AsyncMock, Mock, patch
from aiogram.types import Message, User, Chat
from bot.handlers.common import handle_message

@pytest.mark.asyncio
async def test_handle_message_book_request():
    message = AsyncMock(spec=Message)
    message.text = "посоветуй книгу от тревоги"
    message.from_user = User(id=123, is_bot=False, first_name="Test")
    message.chat = Chat(id=123, type="private")
    message.reply = AsyncMock()

    with patch('bot.handlers.common.contains_keywords', return_value=True) as mock_contains, \
         patch('bot.handlers.common.classify_state', return_value='anxiety'), \
         patch('bot.handlers.common.get_random_book') as mock_get_book:

        mock_book = Mock()
        mock_book.title = "Test Book"
        mock_book.author = "Author"
        mock_book.description = "Desc"
        mock_get_book.return_value = mock_book

        await handle_message(message)

        mock_get_book.assert_called_once_with('anxiety')
        message.reply.assert_awaited_once()

@pytest.mark.asyncio
async def test_handle_message_psychological():
    message = AsyncMock(spec=Message)
    message.text = "мне грустно"
    message.from_user = User(id=123, is_bot=False, first_name="Test")
    message.chat = Chat(id=123, type="private")
    message.reply = AsyncMock()

    with patch('bot.handlers.common.contains_keywords', return_value=False), \
         patch('bot.handlers.common.analyze_sentiment', return_value='negative'), \
         patch('bot.handlers.common.classify_state', return_value='sadness'), \
         patch('bot.handlers.common.get_psychological_response', return_value='Я понимаю твою грусть...') as mock_gen:

        await handle_message(message)

        mock_gen.assert_called_once_with("мне грустно")
        message.reply.assert_awaited_once_with('Я понимаю твою грусть...')