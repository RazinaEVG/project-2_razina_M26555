allowed_types = {"int", "str", "bool"}

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