"""Демонстрационная реализация отдельных детерминированных правил.

Она НЕ заменяет реальный workflow n8n и не формирует контракт 1С.
"""
from collections import defaultdict


def maintenance_interval(mileage, step, tolerance=1000):
    """Вернуть ближайшее положительное кратное шагу ТО в пределах допуска.

    При двух равных ближайших интервалах возвращать None, чтобы не угадывать.
    """
    if step <= 0 or tolerance < 0 or mileage < 0:
        raise ValueError("Пробег, шаг и допуск должны быть допустимыми")
    nearest = []
    lower = max(1, int(mileage // step))
    for index in (lower, lower + 1):
        target = index * step
        if target > 0 and abs(target - mileage) <= tolerance:
            nearest.append((abs(target - mileage), target))
    if not nearest:
        return None
    nearest.sort()
    if len(nearest) > 1 and nearest[0][0] == nearest[1][0]:
        return None
    return nearest[0][1]


def exclude_agreed(works, agreed_codes):
    """Вернуть новые работы, не вошедшие в множество уже согласованных кодов."""
    agreed = {str(code).strip() for code in agreed_codes}
    return [item for item in works if str(item['code']).strip() not in agreed]


def sum_parts_within_defect(items):
    """Суммировать равные детали ВНУТРИ дефекта, не смешивая разные дефекты.

    Каждый элемент содержит defect_id, code, quantity. Порядок первой встречи
    пары (defect_id, code) сохраняется.
    """
    sums = defaultdict(float)
    order = []
    for item in items:
        key = (str(item['defect_id']), str(item['code']))
        quantity = float(item['quantity'])
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if key not in sums:
            order.append(key)
        sums[key] += quantity
    return [{'defect_id': k[0], 'code': k[1], 'quantity': sums[k]} for k in order]
