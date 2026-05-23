from shemas import SORTABLE_FIELDS
from sqlalchemy import desc, asc


def get_sort_column(field: str):
    """获取排序字段，带验证"""
    if field not in SORTABLE_FIELDS:
        raise ValueError(f"无效的排序字段: {field}，可选: {list(SORTABLE_FIELDS.keys())}")
    return SORTABLE_FIELDS[field]

def build_order_by(field: str, order: str = "desc"):
    """构建排序表达式"""
    column = get_sort_column(field)
    return desc(column) if order == "desc" else asc(column)