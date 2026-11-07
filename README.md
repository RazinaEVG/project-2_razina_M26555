# primitive_db

Консольное приложение, имитирующее работу с базой данных.

## Установка и запуск

```bash
uv sync
uv run database
```

## Управление таблицами

Запуск:

```bash
database
```

Команды:

- `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` — создать таблицу. Столбец `ID:int` добавляется автоматически. Типы: `int`, `str`, `bool`.
- `list_tables` — показать список всех таблиц.
- `drop_table <имя_таблицы>` — удалить таблицу.
- `help` — справка.
- `exit` — выход.

Пример:

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
>>>Введите команду: list_tables
- users
>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```

## Демонстрация

[![asciicast](https://asciinema.org/a/N8NoZPI8zFyzCgf1.svg)](https://asciinema.org/a/N8NoZPI8zFyzCgf1)