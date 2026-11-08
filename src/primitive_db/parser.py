def parse_value(value):
    """Парсит значение из строки в соответствующий тип данных."""
    value = value.strip()

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    return int(value)


def parse_condition(condition):
    """Парсит условие вида 'age = 28' в словарь {'age': 28}."""
    result = {}

    for part in condition.split(","):
        key, value = part.split("=", 1)
        result[key.strip()] = parse_value(value)

    return result


def parse_values(values):
    """Парсит строку значений в список."""
    return [parse_value(part) for part in values.split(",")]
