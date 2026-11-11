
from data_layer import Event, Ticket, TicketDetails, User
from exceptions import (
    EventNotFoundError,
    TicketNotFoundError,
    UserNotFoundError,
    ValidationError,
)
from repository_layer import (
    EventRepositoryXML,
    TicketRepositoryJSON,
    UserRepositoryJSON,
)


class InputValidator:
    """Класс для проверки и очистки пользовательского ввода."""

    def validate_name(self, raw_name: str) -> str:
        """Проверяет, что имя состоит только из букв, пробелов или дефисов."""
        cleaned = raw_name.strip()
        if not cleaned:
            raise ValidationError("Имя не может быть пустой строкой.")

        name_for_check = cleaned.replace(" ", "").replace("-", "")
        if not name_for_check.isalpha():
            raise ValidationError(
                "Имя должно состоять только из букв (допускаются пробелы и дефисы)!"
            )
        return cleaned

    def validate_positive_int(self, raw_value: str, field_name: str) -> int:
        """Преобразует строку в положительное целое число или вызывает ошибку."""
        try:
            number = int(raw_value.strip())
        except ValueError as e:
            raise ValidationError(
                f"Поле '{field_name}' должно быть целым числом!"
            ) from e

        if number <= 0:
            raise ValidationError(
                f"Поле '{field_name}' должно быть положительным числом больше нуля!"
            )
        return number


class BookingService:
    """Сервис управления бронированием билетов, мероприятиями и пользователями."""

    def __init__(
        self,
        event_repo: EventRepositoryXML,
        ticket_repo: TicketRepositoryJSON,
        user_repo: UserRepositoryJSON,
    ) -> None:
        """Инициализирует сервис через внедрение зависимостей репозиториев."""
        self._event_repo: EventRepositoryXML = event_repo
        self._ticket_repo: TicketRepositoryJSON = ticket_repo
        self._user_repo: UserRepositoryJSON = user_repo

    def ensure_initial_events(self) -> None:
        """Заполняет базу стартовыми мероприятиями, если XML-файл ещё пуст."""
        if len(self._event_repo.get_all()) == 0:
            self._event_repo.add(Event(1, "Концерт Рок-группы", 50))
            self._event_repo.add(Event(2, "Студенческая вечеринка", 5))
            self._event_repo.add(Event(3, "IT-конференция Python Day", 30))

    def get_available_events(self) -> list[Event]:
        """Возвращает список всех мероприятий."""
        return self._event_repo.get_all()

    def book_ticket(self, event_id: int, user_name: str) -> Ticket:
        """Оформляет бронь билета на мероприятие для указанного пользователя."""
        event = self._event_repo.get_by_id(event_id)
        if event is None:
            raise EventNotFoundError(f"Мероприятие с ID {event_id} не найдено.")

        event.reserve_seat()
        user = self._user_repo.get_or_create_user(user_name)
        self._event_repo.update(event)

        new_ticket = Ticket(None, event.event_id, user.user_id)
        return self._ticket_repo.add(new_ticket)

    def get_user_tickets(self, user_name: str) -> list[TicketDetails]:
        """Возвращает список билетов пользователя вместе с названиями мероприятий."""
        user = self._user_repo.get_user_by_name(user_name)
        if user is None:
            raise UserNotFoundError(
                f"Пользователь '{user_name}' не найден или ещё не делал бронирований."
            )

        raw_tickets = self._ticket_repo.get_tickets_by_user_id(user.user_id)
        details_list: list[TicketDetails] = []

        for ticket in raw_tickets:
            event = self._event_repo.get_by_id(ticket.event_id)
            if event is None:
                event_title = f"Удалённое мероприятие (ID {ticket.event_id})"
            else:
                event_title = event.name

            ticket_id_val = ticket.ticket_id if ticket.ticket_id is not None else 0
            details = TicketDetails(
                ticket_id=ticket_id_val,
                event_id=ticket.event_id,
                event_name=event_title,
                user_name=user.name,
            )
            details_list.append(details)

        return details_list

    def cancel_ticket(self, ticket_id: int) -> None:
        """Отменяет бронь билета по ID и возвращает место в фонд мероприятия."""
        ticket = self._ticket_repo.get_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(f"Билет №{ticket_id} не найден.")

        self._ticket_repo.delete(ticket_id)

        event = self._event_repo.get_by_id(ticket.event_id)
        if event is not None:
            event.release_seat()
            self._event_repo.update(event)

    def rename_user(self, old_name: str, new_name: str) -> User:
        """Изменяет имя существующего пользователя в системе (операция Update)."""
        user = self._user_repo.get_user_by_name(old_name)
        if user is None:
            raise UserNotFoundError(f"Пользователь с именем '{old_name}' не найден.")

        user.name = new_name
        self._user_repo.update(user)
        return user