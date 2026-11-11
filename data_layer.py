"""Модуль сущностей предметной области (Data Layer)."""

from typing import Optional
from exceptions import NoSeatsAvailableError, ValidationError


class Event:
    """Класс, представляющий мероприятие."""

    def __init__(
        self,
        event_id: int,
        name: str,
        total_seats: int,
        available_seats: Optional[int] = None,
    ) -> None:
        """Инициализирует объект мероприятия."""
        self._event_id: int = event_id
        self._name: str = name
        self._total_seats: int = total_seats
        if available_seats is None:
            self._available_seats: int = total_seats
        else:
            self._available_seats = available_seats

    @property
    def event_id(self) -> int:
        """Возвращает уникальный идентификатор мероприятия."""
        return self._event_id

    @property
    def name(self) -> str:
        """Возвращает название мероприятия."""
        return self._name

    @property
    def total_seats(self) -> int:
        """Возвращает общее количество мест на мероприятии."""
        return self._total_seats

    @property
    def available_seats(self) -> int:
        """Возвращает количество доступных для бронирования мест."""
        return self._available_seats

    def reserve_seat(self) -> None:
        """Проверяет наличие свободных мест и уменьшает их количество на единицу."""
        if self._available_seats <= 0:
            raise NoSeatsAvailableError(
                f"На мероприятие '{self._name}' нет свободных мест."
            )
        self._available_seats -= 1

    def release_seat(self) -> None:
        """Освобождает одно место при отмене бронирования билета."""
        if self._available_seats < self._total_seats:
            self._available_seats += 1


class User:
    """Класс, представляющий пользователя системы."""

    def __init__(self, user_id: int, name: str) -> None:
        """Инициализирует объект пользователя."""
        self._user_id: int = user_id
        self._name: str = name

    @property
    def user_id(self) -> int:
        """Возвращает уникальный идентификатор пользователя."""
        return self._user_id

    @property
    def name(self) -> str:
        """Возвращает имя пользователя."""
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """Устанавливает новое имя пользователя после базовой проверки."""
        cleaned = new_name.strip()
        if not cleaned:
            raise ValidationError("Имя пользователя не может быть пустым.")
        self._name = cleaned


class Ticket:
    """Класс, представляющий забронированный билет."""

    def __init__(
        self, ticket_id: Optional[int], event_id: int, user_id: int
    ) -> None:
        """Инициализирует объект билета."""
        self._ticket_id: Optional[int] = ticket_id
        self._event_id: int = event_id
        self._user_id: int = user_id

    @property
    def ticket_id(self) -> Optional[int]:
        """Возвращает идентификатор билета."""
        return self._ticket_id

    @ticket_id.setter
    def ticket_id(self, value: int) -> None:
        """Устанавливает идентификатор билета при сохранении в репозиторий."""
        self._ticket_id = value

    @property
    def event_id(self) -> int:
        """Возвращает идентификатор мероприятия, на которое куплен билет."""
        return self._event_id

    @property
    def user_id(self) -> int:
        """Возвращает идентификатор владельца билета."""
        return self._user_id


class TicketDetails:
    """Класс для хранения сводной информации о билете вместе с названием события."""

    def __init__(
        self,
        ticket_id: int,
        event_id: int,
        event_name: str,
        user_name: str,
    ) -> None:
        """Инициализирует детальное представление билета для вывода в интерфейс."""
        self._ticket_id: int = ticket_id
        self._event_id: int = event_id
        self._event_name: str = event_name
        self._user_name: str = user_name

    @property
    def ticket_id(self) -> int:
        """Возвращает номер билета."""
        return self._ticket_id

    @property
    def event_id(self) -> int:
        """Возвращает ID мероприятия."""
        return self._event_id

    @property
    def event_name(self) -> str:
        """Возвращает название мероприятия."""
        return self._event_name

    @property
    def user_name(self) -> str:
        """Возвращает имя владельца билета."""
        return self._user_name