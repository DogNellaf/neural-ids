import numpy


def get_statistics(alist: list) -> dict:
    """Возвращает сводную статистику по списку значений."""
    if len(alist) == 0:
        return {"total": 0, "max": 0, "min": 0, "mean": 0, "std": 0}
    if len(alist) == 1:
        v = alist[0]
        return {"total": v, "max": v, "min": v, "mean": v, "std": 0}
    return {
        "total": sum(alist),
        "max": max(alist),
        "min": min(alist),
        "mean": float(numpy.mean(alist)),
        "std": float(numpy.std(alist)),
    }
