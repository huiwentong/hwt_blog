"""Tencent Cloud COS (Cloud Object Storage) client wrapper.

Provides convenient methods for uploading, downloading, listing, and deleting
objects in a COS bucket.

Usage:
    from app.cos.cos_client import CosClient

    # Option 1: load credentials from config.json (recommended)
    cos = CosClient.from_config()

    # Option 2: pass credentials directly
    cos = CosClient(
        region="ap-beijing",
        bucket="hw-tblog-1452758724",
    )

    cos.upload_file("local/path.jpg", "remote/path.jpg")
"""

import os
import json
import io
from typing import Optional, BinaryIO
from dataclasses import dataclass, field
from pathlib import Path

from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError


CONFIG_FILENAME = "config.json"


@dataclass
class CosObjectInfo:
    """Information about a COS object."""
    key: str
    size: int
    etag: str
    last_modified: str
    storage_class: str = ""


@dataclass
class CosResult:
    """Standard result wrapper for COS operations."""
    success: bool = True
    message: str = ""
    data: any = None


class CosClient:
    """Simple COS client wrapper with common operations."""

    def __init__(
        self,
        secret_id: str | None = None,
        secret_key: str | None = None,
        region: str = "ap-beijing",
        bucket: str = "hw-tblog-1452758724",
        scheme: str = "https",
        endpoint: str | None = None,
        config_dir: str | os.PathLike | None = None,
    ):
        """
        Initialize COS client.

        Credentials are resolved in this order:
          1. Explicit secret_id / secret_key parameters
          2. config.json file in config_dir (defaults to this file's directory)

        Args:
            secret_id: 腾讯云 API SecretId（未提供则从 config.json 读取）
            secret_key: 腾讯云 API SecretKey（未提供则从 config.json 读取）
            region: COS 地域, 如 ap-beijing
            bucket: COS Bucket 名称
            scheme: http 或 https
            endpoint: 自定义 endpoint, 默认自动拼接
            config_dir: config.json 所在目录, 默认本文件所在目录
        """
        self.region = region
        self.bucket = bucket

        # Resolve credentials
        if secret_id is None or secret_key is None:
            loaded = self._load_credentials(config_dir)
            secret_id = secret_id or loaded.get("secret_id", "")
            secret_key = secret_key or loaded.get("secret_key", "")

        if not secret_id or not secret_key:
            raise ValueError(
                "SecretId and SecretKey must be provided either explicitly "
                "or via config.json"
            )

        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Scheme=scheme,
            Endpoint=endpoint,
        )
        self.client = CosS3Client(config)

    # -- config loading --------------------------------------------------

    @staticmethod
    def _locate_config(config_dir: str | os.PathLike | None = None) -> Path:
        """Locate the config.json file."""
        if config_dir is not None:
            base = Path(os.fspath(config_dir))
        else:
            base = Path(__file__).parent
        return base / CONFIG_FILENAME

    @staticmethod
    def load_config(config_dir: str | os.PathLike | None = None) -> dict:
        """Load and return the raw config.json contents.

        Args:
            config_dir: config.json 所在目录, 默认本文件所在目录

        Returns:
            dict with config.json contents
        """
        config_path = CosClient._locate_config(config_dir)
        if not config_path.is_file():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(str(config_path), "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def from_config(
        cls,
        region: str = "ap-beijing",
        bucket: str = "hw-tblog-1452758724",
        scheme: str = "https",
        endpoint: str | None = None,
        config_dir: str | os.PathLike | None = None,
    ) -> "CosClient":
        """Create CosClient using credentials from config.json.

        Args:
            region: COS 地域
            bucket: COS Bucket 名称
            scheme: http 或 https
            endpoint: 自定义 endpoint
            config_dir: config.json 所在目录, 默认本文件所在目录

        Returns:
            CosClient instance
        """
        cfg = cls.load_config(config_dir)
        return cls(
            secret_id=cfg["SecretId"],
            secret_key=cfg["SecretKey"],
            region=region,
            bucket=bucket,
            scheme=scheme,
            endpoint=endpoint,
        )

    def _load_credentials(self, config_dir=None) -> dict:
        """Load credentials from config.json silently."""
        try:
            cfg = self.load_config(config_dir)
            return {
                "secret_id": cfg.get("SecretId", ""),
                "secret_key": cfg.get("SecretKey", ""),
            }
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return {"secret_id": "", "secret_key": ""}

    # -- upload ---------------------------------------------------------

    def upload_file(
        self,
        local_path: str | os.PathLike,
        cos_key: str,
        progress_callback=None,
    ) -> CosResult:
        """Upload a local file to COS.

        Args:
            local_path: 本地文件路径
            cos_key: COS 上的对象键 (如 images/photo.jpg)
            progress_callback: 可选进度回调(consumed_bytes, total_bytes)

        Returns:
            CosResult with ETag on success
        """
        try:
            local_path = os.fspath(local_path)
            if not os.path.isfile(local_path):
                return CosResult(success=False, message=f"File not found: {local_path}")

            response = self.client.upload_file(
                Bucket=self.bucket,
                LocalFilePath=local_path,
                Key=cos_key,
                EnableMD5=False,
                progress_callback=progress_callback,
            )
            return CosResult(
                success=True,
                message="Upload successful",
                data={"key": cos_key, "etag": response.get("ETag", "")},
            )
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    def upload_bytes(
        self,
        data: bytes,
        cos_key: str,
        content_type: str | None = None,
    ) -> CosResult:
        """Upload bytes data to COS.

        Args:
            data: 二进制数据
            cos_key: COS 上的对象键
            content_type: MIME 类型, 如 image/jpeg

        Returns:
            CosResult
        """
        try:
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=data,
                Key=cos_key,
                ContentType=content_type,
            )
            return CosResult(
                success=True,
                message="Upload successful",
                data={"key": cos_key, "etag": response.get("ETag", "")},
            )
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    def upload_stream(
        self,
        stream: BinaryIO,
        cos_key: str,
        content_type: str | None = None,
    ) -> CosResult:
        """Upload a binary stream to COS.

        Args:
            stream: 已打开的二进制流
            cos_key: COS 上的对象键
            content_type: MIME 类型

        Returns:
            CosResult
        """
        try:
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=stream,
                Key=cos_key,
                ContentType=content_type,
            )
            return CosResult(
                success=True,
                message="Upload successful",
                data={"key": cos_key, "etag": response.get("ETag", "")},
            )
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    # -- download -------------------------------------------------------

    def download_file(
        self,
        cos_key: str,
        local_path: str | os.PathLike,
    ) -> CosResult:
        """Download a file from COS to local path.

        Args:
            cos_key: COS 上的对象键
            local_path: 本地保存路径

        Returns:
            CosResult
        """
        try:
            local_path = os.fspath(local_path)
            os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
            self.client.download_file(
                Bucket=self.bucket,
                Key=cos_key,
                DestFilePath=local_path,
            )
            return CosResult(success=True, message=f"Downloaded to {local_path}")
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    def download_bytes(self, cos_key: str) -> CosResult:
        """Download a COS object as bytes in memory.

        Args:
            cos_key: COS 上的对象键

        Returns:
            CosResult with data containing the bytes
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=cos_key,
            )
            data = response["Body"].get_raw_stream().read()
            return CosResult(success=True, data=data)
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    # -- list -----------------------------------------------------------

    def list_objects(
        self,
        prefix: str = "",
        delimiter: str = "",
        max_keys: int = 1000,
    ) -> CosResult:
        """List objects in the bucket.

        Args:
            prefix: 前缀过滤, 如 "images/"
            delimiter: 分隔符, 通常 "/" 用于模拟目录
            max_keys: 最大返回数量 (最多 1000)

        Returns:
            CosResult with list of CosObjectInfo
        """
        try:
            response = self.client.list_objects(
                Bucket=self.bucket,
                Prefix=prefix,
                Delimiter=delimiter,
                MaxKeys=max_keys,
            )
            objects = []
            contents = response.get("Contents", [])
            for item in contents:
                if item["Key"] == prefix:
                    continue
                objects.append(CosObjectInfo(
                    key=item["Key"],
                    size=item["Size"],
                    etag=item["ETag"].strip(chr(34)),
                    last_modified=item["LastModified"],
                    storage_class=item.get("StorageClass", ""),
                ))

            common_prefixes = [
                p["Prefix"] for p in response.get("CommonPrefixes", [])
            ]

            return CosResult(
                success=True,
                data={
                    "objects": objects,
                    "common_prefixes": common_prefixes,
                    "is_truncated": response.get("IsTruncated") == "true",
                    "next_marker": response.get("NextMarker", ""),
                },
            )
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    # -- delete ---------------------------------------------------------

    def delete_file(self, cos_key: str) -> CosResult:
        """Delete a single object from COS.

        Args:
            cos_key: COS 上的对象键

        Returns:
            CosResult
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=cos_key,
            )
            return CosResult(success=True, message=f"Deleted: {cos_key}")
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    def delete_files(self, cos_keys: list[str]) -> CosResult:
        """Batch delete multiple objects (max 1000).

        Args:
            cos_keys: 要删除的对象键列表

        Returns:
            CosResult
        """
        try:
            objects = [{"Key": k} for k in cos_keys]
            response = self.client.delete_objects(
                Bucket=self.bucket,
                Delete={"Object": objects},
            )
            deleted = [d["Key"] for d in response.get("Deleted", [])]
            errors = response.get("Error", [])
            return CosResult(
                success=len(errors) == 0,
                message=f"Deleted {len(deleted)} objects",
                data={"deleted": deleted, "errors": errors},
            )
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    # -- query ----------------------------------------------------------

    def file_exists(self, cos_key: str) -> bool:
        """Check if an object exists in COS.

        Returns:
            True if exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=cos_key)
            return True
        except CosServiceError as e:
            if e.get_status_code() == 404:
                return False
            raise
        except CosClientError:
            return False

    def get_file_info(self, cos_key: str) -> CosResult:
        """Get metadata of a COS object.

        Args:
            cos_key: COS 上的对象键

        Returns:
            CosResult with metadata dict
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=cos_key,
            )
            info = {
                "key": cos_key,
                "size": response.get("Content-Length", 0),
                "etag": response.get("ETag", "").strip(chr(34)),
                "last_modified": response.get("Last-Modified", ""),
                "content_type": response.get("Content-Type", ""),
                "storage_class": response.get("x-cos-storage-class", ""),
            }
            return CosResult(success=True, data=info)
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    def get_file_url(self, cos_key: str) -> str:
        """Get the public URL of a COS object.

        Returns:
            完整的访问 URL
        """
        return (
            f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{cos_key}"
        )

    def generate_presigned_url(
        self,
        cos_key: str,
        method: str = "GET",
        expires_in_seconds: int = 3600,
    ) -> CosResult:
        """Generate a presigned URL for temporary access.

        Args:
            cos_key: COS 上的对象键
            method: HTTP 方法 (GET/PUT/DELETE/HEAD)
            expires_in_seconds: 过期时间(秒), 默认1小时

        Returns:
            CosResult with presigned URL
        """
        try:
            url = self.client.get_presigned_url(
                Method=method,
                Bucket=self.bucket,
                Key=cos_key,
                Expired=expires_in_seconds,
            )
            return CosResult(success=True, data={"url": url, "expires_in": expires_in_seconds})
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))

    # -- copy -----------------------------------------------------------

    def copy_file(self, source_key: str, target_key: str) -> CosResult:
        """Copy an object within COS.

        Args:
            source_key: 源对象键
            target_key: 目标对象键

        Returns:
            CosResult
        """
        try:
            source = f"{self.bucket}.cos.{self.region}.myqcloud.com/{source_key}"
            response = self.client.copy_object(
                Bucket=self.bucket,
                Key=target_key,
                CopySource=source,
            )
            return CosResult(
                success=True,
                message=f"Copied {source_key} -> {target_key}",
                data=response,
            )
        except (CosClientError, CosServiceError) as e:
            return CosResult(success=False, message=str(e))
