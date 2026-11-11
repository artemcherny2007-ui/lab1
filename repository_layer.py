"""Модуль репозиториев для сериализации и десериализации данных (XML и JSON)."""

from abc import ABC, abstractmethod
import json
from typing import Any, Optional
import xml.etree.ElementTree as ET

from data_layer import Event, Ticket, User
from exceptions import StorageError


class BaseRepository(ABC):
    """Абстрактный базовый класс репозитория с поддержкой операций CRUD."""

    @abstractmethod
    def get_all(self) -> list[Any]:
        """Возвращает список всех записей из хранилища."""

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[Any]:
        """Находит и возвращает запись по её уникальному ID."""

    @abstractmethod
    def add(self, item: Any) -> Any:
        """Добавляет новую запись в хранилище."""

    @abstractmethod
    def update(self, item: Any) -> None:
        """Обновляет существующую запись в хранилище."""

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        """Удаляет запись по её ID и возвращает статус успеха."""


class EventRepositoryXML(BaseRepository):
    """Репозиторий для хранения мероприятий в формате XML."""

    def __init__(self, filename: str = "events.xml") -> None:
        """Инициализирует XML-репозиторий и загружает данные из файла."""
        self._filename: str = filename
        self._events: dict[int, Event] = {}
        self.load_from_xml()

    def load_from_xml(self) -> None:
        """Десериализует мероприятия из XML-файла в оперативную память."""
        try:
            tree = ET.parse(self._filename)
            root = tree.getroot()
            for event_node in root.findall("event"):
                id_node = event_node.find("event_id")
                name_node = event_node.find("name")
                total_node = event_node.find("total_seats")
                avail_node = event_node.find("available_seats")

                if (
                    id_node is None
                    or id_node.text is None
                    or name_node is None
                    or name_node.text is None
                    or total_node is None
                    or total_node.text is None
                    or avail_node is None
                    or avail_node.text is None
                ):
                    raise StorageError(
                        f"Некорректная структура тегов в файле {self._filename}."
                    )

                e_id = int(id_node.text)
                name = name_node.text
                total = int(total_node.text)
                avail = int(avail_node.text)
                self._events[e_id] = Event(e_id, name, total, avail)
        except FileNotFoundError:
            return
        except ET.ParseError as e:
            raise StorageError(f"Файл {self._filename} повреждён (ошибка XML).") from e
        except ValueError as e:
            raise StorageError(
                f"Ошибка типов данных внутри файла {self._filename}."
            ) from e
        except OSError as e:
            raise StorageError(
                f"Ошибка чтения файла {self._filename}: {e}"
            ) from e

    def save_to_xml(self) -> None:
        """Сериализует текущие мероприятия из памяти в XML-файл."""
        root = ET.Element("events")
        for key in self._events:
            event = self._events[key]
            event_node = ET.SubElement(root, "event")

            id_node = ET.SubElement(event_node, "event_id")
            id_node.text = str(event.event_id)

            name_node = ET.SubElement(event_node, "name")
            name_node.text = event.name

            total_node = ET.SubElement(event_node, "total_seats")
            total_node.text = str(event.total_seats)

            avail_node = ET.SubElement(event_node, "available_seats")
            avail_node.text = str(event.available_seats)

        tree = ET.ElementTree(root)
        try:
            tree.write(self._filename, encoding="utf-8", xml_declaration=True)
        except OSError as e:
            raise StorageError(
                f"Не удалось сохранить данные в файл {self._filename}: {e}"
            ) from e

    def get_all(self) -> list[Event]:
        """Возвращает список всех мероприятий."""
        events_list: list[Event] = []
        for key in self._events:
            events_list.append(self._events[key])
        return events_list

    def get_by_id(self, item_id: int) -> Optional[Event]:
        """Возвращает мероприятие по его ID или None, если оно не найдено."""
        if item_id in self._events:
            return self._events[item_id]
        return None

    def add(self, item: Event) -> Event:
        """Добавляет новое мероприятие и сохраняет изменения в XML."""
        self._events[item.event_id] = item
        self.save_to_xml()
        return item

    def update(self, item: Event) -> None:
        """Обновляет данные мероприятия и перезаписывает XML-файл."""
        self._events[item.event_id] = item
        self.save_to_xml()

    def delete(self, item_id: int) -> bool:
        """Удаляет мероприятие по ID из словаря и XML-файла."""
        if item_id in self._events:
            del self._events[item_id]
            self.save_to_xml()
            return True
        return False


class TicketRepositoryJSON(BaseRepository):
    """Репозиторий для хранения билетов в формате JSON."""

    def __init__(self, filename: str = "tickets.json") -> None:
        """Инициализирует JSON-репозиторий билетов и загружает данные."""
        self._filename: str = filename
        self._tickets: list[Ticket] = []
        self._next_ticket_id: int = 1
        self.load_from_json()

    def load_from_json(self) -> None:
        """Десериализует список билетов из JSON-файла."""
        try:
            with open(self._filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                for item in data:
                    t_id = int(item["ticket_id"])
                    e_id = int(item["event_id"])
                    u_id = int(item["user_id"])
                    ticket = Ticket(t_id, e_id, u_id)
                    self._tickets.append(ticket)
                    if t_id >= self._next_ticket_id:
                        self._next_ticket_id = t_id + 1
        except FileNotFoundError:
            return
        except json.JSONDecodeError as e:
            raise StorageError(f"Файл {self._filename} повреждён (ошибка JSON).") from e
        except (KeyError, ValueError, TypeError) as e:
            raise StorageError(
                f"Некорректный формат данных в файле {self._filename}."
            ) from e
        except OSError as e:
            raise StorageError(
                f"Ошибка чтения файла {self._filename}: {e}"
            ) from e

    def save_to_json(self) -> None:
        """Сериализует список всех билетов в JSON-файл."""
        data: list[dict[str, Any]] = []
        for ticket in self._tickets:
            ticket_dict: dict[str, Any] = {}
            ticket_dict["ticket_id"] = ticket.ticket_id
            ticket_dict["event_id"] = ticket.event_id
            ticket_dict["user_id"] = ticket.user_id
            data.append(ticket_dict)

        try:
            with open(self._filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except OSError as e:
            raise StorageError(
                f"Не удалось записать данные в файл {self._filename}: {e}"
            ) from e

    def get_all(self) -> list[Ticket]:
        """Возвращает копию списка всех билетов."""
        return list(self._tickets)

    def get_by_id(self, item_id: int) -> Optional[Ticket]:
        """Находит билет по его номеру или возвращает None."""
        for ticket in self._tickets:
            if ticket.ticket_id == item_id:
                return ticket
        return None

    def add(self, item: Ticket) -> Ticket:
        """Присваивает билету уникальный ID, добавляет в список и сохраняет в JSON."""
        item.ticket_id = self._next_ticket_id
        self._next_ticket_id += 1
        self._tickets.append(item)
        self.save_to_json()
        return item

    def update(self, item: Ticket) -> None:
        """Обновляет существующий билет в списке и сохраняет JSON-файл."""
        for i in range(len(self._tickets)):
            if self._tickets[i].ticket_id == item.ticket_id:
                self._tickets[i] = item
                self.save_to_json()
                return

    def delete(self, item_id: int) -> bool:
        """Удаляет билет по его ID (используется при отмене брони)."""
        for ticket in self._tickets:
            if ticket.ticket_id == item_id:
                self._tickets.remove(ticket)
                self.save_to_json()
                return True
        return False

    def get_tickets_by_user_id(self, user_id: int) -> list[Ticket]:
        """Возвращает список всех билетов, принадлежащих конкретному пользователю."""
        user_tickets: list[Ticket] = []
        for ticket in self._tickets:
            if ticket.user_id == user_id:
                user_tickets.append(ticket)
        return user_tickets


class UserRepositoryJSON(BaseRepository):
    """Репозиторий для хранения пользователей в формате JSON."""

    def __init__(self, filename: str = "users.json") -> None:
        """Инициализирует JSON-репозиторий пользователей и загружает данные."""
        self._filename: str = filename
        self._users: dict[int, User] = {}
        self._next_user_id: int = 1
        self.load_from_json()

    def load_from_json(self) -> None:
        """Десериализует данные пользователей из JSON-файла."""
        try:
            with open(self._filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                for item in data:
                    u_id = int(item["user_id"])
                    name = str(item["name"])
                    user = User(u_id, name)
                    self._users[u_id] = user
                    if u_id >= self._next_user_id:
                        self._next_user_id = u_id + 1
        except FileNotFoundError:
            return
        except json.JSONDecodeError as e:
            raise StorageError(f"Файл {self._filename} повреждён (ошибка JSON).") from e
        except (KeyError, ValueError, TypeError) as e:
            raise StorageError(
                f"Некорректный формат данных в файле {self._filename}."
            ) from e
        except OSError as e:
            raise StorageError(
                f"Ошибка чтения файла {self._filename}: {e}"
            ) from e

    def save_to_json(self) -> None:
        """Сериализует словарь пользователей в JSON-файл."""
        data: list[dict[str, Any]] = []
        for key in self._users:
            user = self._users[key]
            user_dict: dict[str, Any] = {}
            user_dict["user_id"] = user.user_id
            user_dict["name"] = user.name
            data.append(user_dict)

        try:
            with open(self._filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except OSError as e:
            raise StorageError(
                f"Не удалось записать данные в файл {self._filename}: {e}"
            ) from e

    def get_all(self) -> list[User]:
        """Возвращает список всех зарегистрированных пользователей."""
        users_list: list[User] = []
        for key in self._users:
            users_list.append(self._users[key])
        return users_list

    def get_by_id(self, item_id: int) -> Optional[User]:
        """Возвращает пользователя по его ID или None."""
        if item_id in self._users:
            return self._users[item_id]
        return None

    def add(self, item: User) -> User:
        """Сохраняет нового пользователя в словарь и записывает изменения в JSON."""
        self._users[item.user_id] = item
        self.save_to_json()
        return item

    def update(self, item: User) -> None:
        """Обновляет данные существующего пользователя в JSON-файле."""
        self._users[item.user_id] = item
        self.save_to_json()

    def delete(self, item_id: int) -> bool:
        """Удаляет пользователя по ID из базы."""
        if item_id in self._users:
            del self._users[item_id]
            self.save_to_json()
            return True
        return False

    def get_user_by_name(self, name: str) -> Optional[User]:
        """Ищет пользователя по имени (без учёта регистра)."""
        target = name.strip().lower()
        for key in self._users:
            user = self._users[key]
            if user.name.lower() == target:
                return user
        return None

    def get_or_create_user(self, name: str) -> User:
        """Возвращает существующего пользователя по имени или создаёт нового."""
        existing = self.get_user_by_name(name)
        if existing is not None:
            return existing

        new_user = User(self._next_user_id, name.strip())
        self._next_user_id += 1
        return self.add(new_user)