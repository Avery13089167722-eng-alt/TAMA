from typing import Dict, Optional
import os
import mimetypes

import requests


class LLMApiClient:
    """云端大模型 API 调用封装。"""

    def __init__(
        self,
        base_url: str,
        api_path: str = "/v1/tongue-analyze",
        text_api_path: str = "/v1/text-chat",
        timeout: int = 90,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_path = api_path
        self.text_api_path = text_api_path
        self.timeout = timeout

    def analyze_tongue_image(
        self,
        image_path: str,
        user_note: str = "",
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict:
        import traceback

        headers = {}
        if extra_headers:
            headers.update(extra_headers)

        question = user_note or "请从中医角度详细解读这张舌苔，包括体质分析和调理建议。"
        form_data = {
            "question": question,
            "max_new_tokens": "512",
        }
        url = f"{self.base_url}{self.api_path}"

        # 验证文件存在性和大小
        if not os.path.exists(image_path):
            error_msg = f"image file not found: {image_path}"
            print(f"[ERROR] {error_msg}")
            traceback.print_exc()
            raise FileNotFoundError(error_msg)

        file_size = os.path.getsize(image_path)
        if file_size <= 0:
            error_msg = f"image file empty: {image_path}"
            print(f"[ERROR] {error_msg}")
            traceback.print_exc()
            raise FileNotFoundError(error_msg)

        # 检测 MIME 类型
        mime, _ = mimetypes.guess_type(image_path)
        mime = mime or "application/octet-stream"

        print(f"[INFO] Uploading image: {image_path}, size: {file_size}, mime: {mime}")
        print(f"[INFO] API URL: {url}")

        try:
            with open(image_path, "rb") as f:
                files = {"file": (os.path.basename(image_path), f, mime)}
                resp = requests.post(url, data=form_data, files=files, headers=headers, timeout=self.timeout)

            print(f"[INFO] Response status: {resp.status_code}")
            print(f"[INFO] Response headers: {dict(resp.headers)}")

            resp.raise_for_status()
            result = resp.json()
            print(f"[INFO] Response data: {result}")
            return result
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            traceback.print_exc()
            raise
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            traceback.print_exc()
            raise

    def text_chat(
        self,
        question: str,
        extra_headers: Optional[Dict[str, str]] = None,
        max_new_tokens: int = 512,
    ) -> Dict:
        headers = {}
        if extra_headers:
            headers.update(extra_headers)

        payload = {"question": question, "max_new_tokens": max_new_tokens}
        url = f"{self.base_url}{self.text_api_path}"
        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

