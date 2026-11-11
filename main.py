"""Точка входа в приложение и слой пользовательского интерфейса (Presentation Layer)."""

from exceptions import BookingError, StorageError
from repository_layer import (
    EventRepositoryXML,
    TicketRepositoryJSON,
    UserRepositoryJSON,
)
from service_layer import BookingService, InputValidator


class ConsoleApp:
    """Класс консольного интерфейса взаимодействия с пользователем."""

    def __init__(
        self, service: BookingService, validator: InputValidator
    ) -> None:
        """Инициализирует консольное приложение сервисом и валидатором."""
        self._service: BookingService = service
        self._validator: InputValidator = validator

    def _show_events(self) -> None:
        """Выводит в консоль список всех доступных мероприятий."""
        events = self._service.get_available_events()
        if not events:
            print("Список мероприятий пуст.")
            return

        print("\n--- Доступные мероприятия ---")
        for event in events:
            print(
                f"ID: {event.event_id} | {event.name} | "
                f"Свободных мест: {event.available_seats}/{event.total_seats}"
            )

    def _handle_book_ticket(self) -> None:
        """Обрабатывает сценарий бронирования нового билета."""
        raw_event_id = input("Введите ID мероприятия: ")
        event_id = self._validator.validate_positive_int(
            raw_event_id, "ID мероприятия"
        )

        raw_name = input("Введите ваше имя: ")
        user_name = self._validator.validate_name(raw_name)

        ticket = self._service.book_ticket(event_id, user_name)
        print(f"Успех! Билет №{ticket.ticket_id} успешно забронирован.")

    def _handle_user_tickets(self) -> None:
        """Обрабатывает сценарий просмотра билетов пользователя."""
        raw_name = input("Введите ваше имя: ")
        user_name = self._validator.validate_name(raw_name)

        tickets = self._service.get_user_tickets(user_name)
        if not tickets:
            print("У вас пока нет активных билетов.")
            return

        print(f"\n--- Билеты пользователя {user_name} ---")
        for item in tickets:
            print(
                f"Билет №{item.ticket_id} | Мероприятие: {item.event_name} "
                f"(ID события: {item.event_id})"
            )

    def _handle_cancel_ticket(self) -> None:
        """Обрабатывает сценарий отмены бронирования (удаление билета)."""
        raw_ticket_id = input("Введите номер билета для отмены брони: ")
        ticket_id = self._validator.validate_positive_int(
            raw_ticket_id, "Номер билета"
        )

        self._service.cancel_ticket(ticket_id)
        print(f"Бронь билета №{ticket_id} успешно отменена. Место освобождено.")

    def _handle_rename_user(self) -> None:
        """Обрабатывает сценарий изменения имени пользователя."""
        raw_old = input("Введите текущее имя пользователя: ")
        old_name = self._validator.validate_name(raw_old)

        raw_new = input("Введите новое имя пользователя: ")
        new_name = self._validator.validate_name(raw_new)

        updated_user = self._service.rename_user(old_name, new_name)
        print(
            f"Данные обновлены! Новое имя пользователя (ID {updated_user.user_id}): "
            f"{updated_user.name}"
        )

    def run(self) -> None:
        """Запускает главный цикл консольного меню программы."""
        while True:
            print("\n=== Система бронирования билетов ===")
            print("1. Список мероприятий")
            print("2. Забронировать билет")
            print("3. Мои билеты")
            print("4. Отменить бронь билета")
            print("5. Изменить имя пользователя")
            print("6. Выход")

            choice = input("Ваш выбор: ").strip()

            try:
                if choice == "1":
                    self._show_events()
                elif choice == "2":
                    self._handle_book_ticket()
                elif choice == "3":
                    self._handle_user_tickets()
                elif choice == "4":
                    self._handle_cancel_ticket()
                elif choice == "5":
                    self._handle_rename_user()
                elif choice == "6":
                    print("Работа программы завершена.")
                    break
                else:
                    print("Неверный пункт меню. Выберите число от 1 до 6.")
            except BookingError as e:
                print(f"Ошибка: {e}")


def main() -> None:
    """Создаёт объекты всех слоёв и запускает приложение."""
    try:
        event_repo = EventRepositoryXML()
        ticket_repo = TicketRepositoryJSON()
        user_repo = UserRepositoryJSON()

        service = BookingService(event_repo, ticket_repo, user_repo)
        service.ensure_initial_events()

        validator = InputValidator()
        app = ConsoleApp(service, validator)
        app.run()
    except StorageError as e:
        print(f"Критическая ошибка хранилища данных: {e}")


if __name__ == "__main__":
    main()