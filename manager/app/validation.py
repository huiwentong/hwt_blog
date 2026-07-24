"""Validation rules for each data type."""

from typing import Optional


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, msg: str):
        self.errors.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)


def validate_article(
    title: str,
    summary: str,
    content: str,
    category: str,
    tags: str,
) -> ValidationResult:
    result = ValidationResult()

    if not title.strip():
        result.add_error("【标题】不能为空")
    if not summary.strip():
        result.add_error("【摘要】不能为空")
    if not content.strip():
        result.add_error("【正文】不能为空")
    if not category.strip():
        result.add_error("【分类】不能为空，请选择一个分类")
    if not tags.strip():
        result.add_warning("【标签】未填入，建议填写标签以便检索")

    return result


def validate_tool(
    name: str,
    description: str,
    url: str,
    category: str,
) -> ValidationResult:
    result = ValidationResult()

    if not name.strip():
        result.add_error("【工具名称】不能为空")
    if not description.strip():
        result.add_error("【工具描述】不能为空")
    if not url.strip():
        result.add_error("【工具链接】不能为空")
    elif not url.startswith("https://"):
        result.add_warning("【工具链接】建议以 https:// 开始")
    if not category.strip():
        result.add_error("【工具分类】不能为空，请选择一个分类")

    return result


def validate_media(
    title: str,
    type_: str,
) -> ValidationResult:
    result = ValidationResult()

    if not title.strip():
        result.add_error("【媒体标题】不能为空")
    if not type_:
        result.add_error("【媒体类型】不能为空，请选择一个类型")

    return result
