from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data

allowed_types = {"int", "str", "bool"}


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает таблицу. Возвращает обновленные метаданные или None при ошибке."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    new_columns = ["ID:int"]
    for column in columns:
        if column.count(":") != 1:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None

        name, data_type = column.split(":")

        if not name or data_type not in allowed_types:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None

        if name == "ID":
            continue

        new_columns.append(column)

    metadata[table_name] = new_columns

    print(
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {", ".join(new_columns)}'
    )
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу. Возвращает обновленные метаданные или None при ошибке."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Печатает список всех таблиц."""
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет запись. Возвращает данные таблицы или None при ошибке."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    table_columns = metadata[table_name][1:]

    if len(values) != len(table_columns):
        print(
            f"Ошибка: Количество значений не соответствует количеству столбцов "
            f'в таблице "{table_name}".'
        )
        return None 

    record = {}
    for column, value in zip(table_columns, values):
        name, data_type = column.split(":") 

        if data_type == "int" and type(value) is not int:
            print(f"Ошибка: Столбец '{name}' должен содержать int.")
            return None

        if data_type == "str" and type(value) is not str:
            print(f"Ошибка: Столбец '{name}' должен содержать str.")
            return None 

        if data_type == "bool" and type(value) is not bool:
            print(f"Ошибка: Столбец '{name}' должен содержать bool.")
            return None 

        record[name] = value

    table_data = load_table_data(table_name)
    record["ID"] = max((row["ID"] for row in table_data), default=0) + 1
    table_data.append(record)
    print(
        f'Запись с ID={record["ID"]} успешно добавлена '
        f'в таблицу "{table_name}".'
    )
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает записи, соответствующие условию where_clause."""
    if where_clause is None:
        return table_data

    result = []
    for record in table_data:
        if all(record.get(k) == v for k, v in where_clause.items()):
            result.append(record)

    return result


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи, соответствующие условию where_clause."""
    for record in table_data:
        if all(record.get(k) == v for k, v in where_clause.items()):
            record.update(set_clause)

    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет записи, соответствующие условию where_clause."""
    result = []
    for record in table_data:
        if not all(record.get(k) == v for k, v in where_clause.items()):
            result.append(record)
   
    return result
