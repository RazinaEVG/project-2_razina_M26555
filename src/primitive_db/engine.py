import os
import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import parse_condition, parse_values
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

META_FILE = "db_meta.json"


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) "
        "- создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Главный цикл программы."""
    print("***База данных***")
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command, *params = args

        match command:
            case "create_table":
                if len(params) < 2:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                result = create_table(metadata, params[0], params[1:])
                if result is not None:
                    save_metadata(META_FILE, result)
            case "drop_table":
                if len(params) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                result = drop_table(metadata, params[0])
                if result is not None:
                    save_metadata(META_FILE, result)
                    data_file = os.path.join("data", f"{params[0]}.json")
                    if os.path.exists(data_file):
                        os.remove(data_file)
            case "list_tables":
                list_tables(metadata)
            case "insert" | "select" | "update" | "delete":
                run_crud(metadata, command, user_input)
            case "info":
                if len(params) != 1:
                    print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                    continue
                run_info(metadata, params[0])
            case "help":
                print_help()
            case "exit":
                break
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")


def get_column_names(metadata, table_name):
    """Возвращает имена столбцов таблицы: ['ID', 'name', 'age']."""
    return [column.split(":")[0] for column in metadata[table_name]]


def print_table(metadata, table_name, rows):
    """Выводит записи таблицей с помощью prettytable."""
    table = PrettyTable()
    table.field_names = get_column_names(metadata, table_name)
    for row in rows:
        table.add_row([row[name] for name in table.field_names])
    print(table)


def table_exists(metadata, table_name):
    """Печатает ошибку, если таблицы нет."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


def run_insert(metadata, user_input):
    # insert into users values ("Sergei", 28, true)
    _, _, table_name, rest = user_input.split(maxsplit=3)
    values = parse_values(rest.removeprefix("values").strip().strip("()"))
    table_data = insert(metadata, table_name, values)
    if table_data is not None:
        save_table_data(table_name, table_data)


def run_select(metadata, user_input):
    # select from users  /  select from users where age = 28
    parts = user_input.split(maxsplit=4)
    table_name = parts[2]
    where = parse_condition(parts[4]) if len(parts) == 5 else None
    if table_exists(metadata, table_name):
        rows = select(load_table_data(table_name), where)
        print_table(metadata, table_name, rows)


def run_update(metadata, user_input):
    # update users set age = 29 where name = "Sergei"
    _, table_name, _, rest = user_input.split(maxsplit=3)
    set_text, where_text = rest.split(" where ")
    if not table_exists(metadata, table_name):
        return
    where = parse_condition(where_text)
    table_data = load_table_data(table_name)
    ids = [row["ID"] for row in select(table_data, where)]
    update(table_data, parse_condition(set_text), where)
    save_table_data(table_name, table_data)
    for i in ids:
        print(f'Запись с ID={i} в таблице "{table_name}" успешно обновлена.')


def run_delete(metadata, user_input):
    # delete from users where ID = 1
    _, _, table_name, _, where_text = user_input.split(maxsplit=4)
    if not table_exists(metadata, table_name):
        return
    where = parse_condition(where_text)
    table_data = load_table_data(table_name)
    ids = [row["ID"] for row in select(table_data, where)]
    save_table_data(table_name, delete(table_data, where))
    for i in ids:
        print(f'Запись с ID={i} успешно удалена из таблицы "{table_name}".')


def run_info(metadata, table_name):
    if table_exists(metadata, table_name):
        print(f"Таблица: {table_name}")
        print(f"Столбцы: {', '.join(metadata[table_name])}")
        print(f"Количество записей: {len(load_table_data(table_name))}")


def run_crud(metadata, command, user_input):
    """Вызывает обработчик CRUD-команды и ловит ошибки ввода."""
    handlers = {
        "insert": run_insert,
        "select": run_select,
        "update": run_update,
        "delete": run_delete,
    }
    try:
        handlers[command](metadata, user_input)
    except (ValueError, IndexError):
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")