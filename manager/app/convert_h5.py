import os
import re
import base64
import mimetypes
from pathlib import Path

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
}


def file_to_data_uri(path: Path) -> str:
    """转换图片为 base64 data uri"""
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "application/octet-stream"
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def replace_image_reference(
    html: str,
    root_dir
) -> str:
    root_dir = Path(root_dir).resolve()
    def replace(match):
        prefix = match.group(1)
        src = match.group(2)
        # 跳过网络资源
        if src.startswith(
            (
                "http://",
                "https://",
                "data:",
                "//"
            )
        ):
            return match.group(0)
        image_path = (
            root_dir / src
        ).resolve()
        if not image_path.exists():
            print(
                f"[missing] {image_path}"
            )
            return match.group(0)
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            return match.group(0)
        print(
            f"[embed] {src}"
        )
        data_uri = file_to_data_uri(
            image_path
        )
        return (
            f'{prefix}{data_uri}"'
        )

    # img src
    html = re.sub(
        r'(\s(?:src|href)\s*=\s*["\'])([^"\']+)',
        replace,
        html
    )


    # css url()
    def css_replace(match):
        src = match.group(1)
        if src.startswith(
            (
                "http://",
                "https://",
                "data:"
            )
        ):
            return match.group(0)
        image_path = (
            root_dir / src
        ).resolve()
        if not image_path.exists():
            print(
                f"[missing] {image_path}"
            )
            return match.group(0)
        print(
            f"[embed css] {src}"
        )
        return (
            "url("
            + file_to_data_uri(image_path)
            + ")"
        )
    html = re.sub(
        r'url\(["\']?([^)"\']+)["\']?\)',
        css_replace,
        html
    )
    return html


def convert_h5(h5_path:str, out_name = None) -> str:
    h5_file = Path(h5_path)
    html = h5_file.read_text(encoding="utf-8")
    result = replace_image_reference(html,str(h5_file.parent))
    if out_name:
        output = h5_file.with_name(out_name)
        output.write_text(result,encoding="utf-8")
        print(f"done: {output}")
        return ''
    else:
        return result
