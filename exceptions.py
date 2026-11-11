"""Модуль пользовательских исключений для системы бронирования билетов."""


class BookingError(Exception):
    """Базовый класс для всех исключений системы бронирования."""


class StorageError(BookingError):
    """Ошибка чтения, записи или повреждения файла хранилища (XML/JSON)."""


class EventNotFoundError(BookingError):
    """Ошибка: запрашиваемое мероприятие не найдено в базе."""


class NoSeatsAvailableError(BookingError):
    """Ошибка: на выбранное мероприятие нет свободных мест."""


class UserNotFoundError(BookingError):
    """Ошибка: пользователь не найден в базе данных."""


class TicketNotFoundError(BookingError):
    """Ошибка: билет с указанным ID не найден."""


class ValidationError(BookingError):
    """Ошибка валидации пользовательского ввода."""