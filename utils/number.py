def round_number(value: int | float, ndigits: int) -> int | float:
    """
    :param value: Число (float или int), которое нужно округлить
    :param ndigits: Число для округления
    :return: Строка с числом в удобном формате
    """
    rounded_value: float = round(value, ndigits)

    # Проверяем, является ли число целым
    if rounded_value == int(rounded_value):
        return int(rounded_value)
    else:
        # return f"{rounded_value}".replace('.', ',')
        return rounded_value
