import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()


DEFAULT_BASE_URL = "https://api.m-team.cc/api"


def format_size(size_bytes):
    if size_bytes is None:
        return "?"
    try:
        n = int(size_bytes)
    except (ValueError, TypeError):
        return str(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} PB"


class MTeamAPI:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.environ.get("MTEAM_API_KEY", "")
        self.base_url = (base_url or os.environ.get("MTEAM_API_BASE", DEFAULT_BASE_URL)).rstrip("/")
        if not self.api_key:
            raise RuntimeError(
                "MTEAM_API_KEY 未设置。请设置环境变量或在代码中传入 api_key 参数。"
            )

    def _headers(self, json_content=True):
        h = {"x-api-key": self.api_key}
        if json_content:
            h["Content-Type"] = "application/json"
        return h

    def search(self, keyword, mode="normal", page_number=1, page_size=20):
        """搜索 torrent，返回 (data_dict, error_message)。"""
        url = f"{self.base_url}/torrent/search"
        body = {
            "keyword": keyword,
            "mode": mode,
            "pageNumber": page_number,
            "pageSize": page_size,
        }
        resp = requests.post(url, json=body, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code")
        message = data.get("message", "")
        payload = data.get("data")

        if str(code) != "0" and str(message).upper() != "SUCCESS":
            return None, f"API 错误 (code={code}): {message}"

        if isinstance(payload, dict):
            items = payload.get("list") or payload.get("data") or payload.get("torrents") or []
            total = payload.get("total") or payload.get("totalCount") or len(items)
        elif isinstance(payload, list):
            items = payload
            total = len(payload)
        else:
            return None, f"无法解析返回格式:\n{data}"

        return {"items": items, "total": total, "page": page_number, "page_size": page_size}, None

    def detail(self, torrent_id):
        """获取 torrent 详情，返回 (data_dict, error_message)。"""
        url = f"{self.base_url}/torrent/detail"
        headers = {k: v for k, v in self._headers().items() if k != "Content-Type"}
        resp = requests.post(url, data={"id": torrent_id}, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code")
        message = data.get("message", "")
        payload = data.get("data")

        if payload is None:
            return None, f"API 错误 (code={code}): {message}"

        return payload if isinstance(payload, dict) else {}, None

    def download(self, torrent_id, download_dir="./seed"):
        """下载 .torrent 文件，返回 (filepath, error_message)。"""
        # 获取下载 token
        token_url = f"{self.base_url}/torrent/genDlToken"
        token_headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-api-key": self.api_key,
        }
        resp = requests.post(token_url, data={"id": torrent_id}, headers=token_headers, timeout=15)
        resp.raise_for_status()
        token_data = resp.json()

        if str(token_data.get("message", "")).upper() != "SUCCESS" or not token_data.get("data"):
            return None, f"获取下载 token 失败: {token_data}"

        download_url = token_data["data"]

        # 尝试获取种子名称
        torrent_name = torrent_id
        try:
            detail_headers = {k: v for k, v in self._headers().items() if k != "Content-Type"}
            dresp = requests.post(
                f"{self.base_url}/torrent/detail",
                data={"id": torrent_id},
                headers=detail_headers,
                timeout=15,
            )
            dresp.raise_for_status()
            ddata = dresp.json()
            raw_name = (ddata.get("data") or {}).get("name") or ""
            if raw_name:
                torrent_name = raw_name
        except Exception:
            pass

        dotted = torrent_name.replace(" ", ".")
        safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", dotted).strip(".")
        if not safe_name:
            safe_name = torrent_id
        filename = f"[M-TEAM]{safe_name}.torrent"
        os.makedirs(download_dir, exist_ok=True)
        output_path = os.path.abspath(os.path.join(download_dir, filename))

        dl_resp = requests.get(download_url, stream=True, timeout=60)
        dl_resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in dl_resp.iter_content(chunk_size=128 * 1024):
                if chunk:
                    f.write(chunk)

        return output_path, None
