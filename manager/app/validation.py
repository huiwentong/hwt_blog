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
        result.add_error("銆愭爣棰樸€戜笉鑳戒负绌?)
    if not summary.strip():
        result.add_error("銆愭憳瑕併€戜笉鑳戒负绌?)
    if not content.strip():
        result.add_error("銆愭鏂囥€戜笉鑳戒负绌?)
    if not category.strip():
        result.add_error("銆愬垎绫汇€戜笉鑳戒负绌猴紝璇烽€夋嫨涓€涓垎绫?)
    if not tags.strip():
        result.add_warning("銆愭爣绛俱€戞湭濉啓锛屽缓璁坊鍔犳爣绛句互渚挎绱?)

    return result


def validate_tool(
    name: str,
    description: str,
    url: str,
    category: str,
) -> ValidationResult:
    result = ValidationResult()

    if not name.strip():
        result.add_error("銆愬伐鍏峰悕绉般€戜笉鑳戒负绌?)
    if not description.strip():
        result.add_error("銆愬伐鍏锋弿杩般€戜笉鑳戒负绌?)
    if not url.strip():
        result.add_error("銆愬伐鍏烽摼鎺ャ€戜笉鑳戒负绌?)
    elif not url.startswith(("http://", "https://")):
        result.add_warning("銆愬伐鍏烽摼鎺ャ€戝缓璁互 http:// 鎴?https:// 寮€澶?)
    if not category.strip():
        result.add_error("銆愬伐鍏峰垎绫汇€戜笉鑳戒负绌猴紝璇烽€夋嫨涓€涓垎绫?)

    return result


def validate_media(
    title: str,
    type_: str,
) -> ValidationResult:
    result = ValidationResult()

    if not title.strip():
        result.add_error("銆愬獟浣撴爣棰樸€戜笉鑳戒负绌?)
    if not type_:
        result.add_error("銆愬獟浣撶被鍨嬨€戜笉鑳戒负绌猴紝璇烽€夋嫨涓€涓被鍨?)

    return result