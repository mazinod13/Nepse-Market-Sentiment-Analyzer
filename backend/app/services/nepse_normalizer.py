
import asyncio
import json
import pathlib
import time
from datetime import date

import httpx
import pywasm

# ---------------------------------------------------------------------------
# Paths — all data files live next to this script
# ---------------------------------------------------------------------------

_HERE = pathlib.Path(__file__).resolve().parent / "data"
WASM_PATH       = _HERE / "css.wasm"
ENDPOINTS_PATH  = _HERE / "API_ENDPOINTS.json"
DUMMY_DATA_PATH = _HERE / "DUMMY_DATA.json"
HEADERS_PATH    = _HERE / "HEADERS.json"

BASE_URL   = "https://www.nepalstock.com"
TOKEN_URL  = "/api/authenticate/prove"
TOKEN_TTL  = 45   # seconds
MAX_RETRY  = 3


# ---------------------------------------------------------------------------
# Load data files
# ---------------------------------------------------------------------------

def _load_json(path: pathlib.Path) -> any:
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Token parser (css.wasm)
# ---------------------------------------------------------------------------

class _TokenParser:
    def __init__(self):
        self._rt  = pywasm.core.Runtime()
        self._mod = self._rt.instance_from_file(str(WASM_PATH))

    def _call(self, fn: str, args: list) -> int:
        return self._rt.invocate(self._mod, fn, args)[0]

    def parse(self, resp: dict) -> tuple[str, str]:
        s = [resp[f"salt{i}"] for i in range(1, 6)]

        # access token indices
        n = self._call("cdx", [s[0], s[1], s[2], s[3], s[4]])
        l = self._call("rdx", [s[0], s[1], s[3], s[2], s[4]])
        o = self._call("bdx", [s[0], s[1], s[3], s[2], s[4]])
        p = self._call("ndx", [s[0], s[1], s[3], s[2], s[4]])
        q = self._call("mdx", [s[0], s[1], s[3], s[2], s[4]])

        # refresh token indices
        a = self._call("cdx", [s[1], s[0], s[2], s[4], s[3]])
        b = self._call("rdx", [s[1], s[0], s[2], s[3], s[4]])
        c = self._call("bdx", [s[1], s[0], s[3], s[2], s[4]])
        d = self._call("ndx", [s[1], s[0], s[3], s[2], s[4]])
        e = self._call("mdx", [s[1], s[0], s[3], s[2], s[4]])

        at = resp["accessToken"]
        rt = resp["refreshToken"]

        access  = at[0:n] + at[n+1:l] + at[l+1:o] + at[o+1:p] + at[p+1:q] + at[q+1:]
        refresh = rt[0:a] + rt[a+1:b] + rt[b+1:c] + rt[c+1:d] + rt[d+1:e] + rt[e+1:]
        return access, refresh


# ---------------------------------------------------------------------------
# Token manager
# ---------------------------------------------------------------------------

class _TokenManager:
    def __init__(self, parser: _TokenParser):
        self._parser       = parser
        self.access_token  = None
        self.salts         = []
        self._ts           = None
        self._busy         = asyncio.Event()
        self.update_done   = asyncio.Event()
        self.update_done.set()

    def _valid(self) -> bool:
        return self._ts is not None and (int(time.time()) - self._ts) < TOKEN_TTL

    async def get_token(self, client: httpx.AsyncClient) -> str:
        if not self._valid():
            await self._refresh(client)
        return self.access_token

    async def update(self, client: httpx.AsyncClient):
        await self._refresh(client)

    async def _refresh(self, client: httpx.AsyncClient):
        if self._busy.is_set():
            await self.update_done.wait()
            return
        self._busy.set()
        self.update_done.clear()
        try:
            resp = await client.get(f"{BASE_URL}{TOKEN_URL}")
            resp.raise_for_status()
            data = resp.json()
            self.access_token, _ = self._parser.parse(data)
            self.salts = [int(data[f"salt{i}"]) for i in range(1, 6)]
            self._ts   = int(data["serverTime"] / 1000)
        finally:
            self._busy.clear()
            self.update_done.set()


# ---------------------------------------------------------------------------
# Sentinel
# ---------------------------------------------------------------------------

class _TokenExpired(Exception):
    pass


# ---------------------------------------------------------------------------
# Main client
# ---------------------------------------------------------------------------

class NepseClient:
    def __init__(self, verify_tls: bool = False):
        self._ep          = _load_json(ENDPOINTS_PATH)
        self._dummy_data  = _load_json(DUMMY_DATA_PATH)
        self._headers     = _load_json(HEADERS_PATH)
        self._headers["Host"]    = BASE_URL.replace("https://", "")
        self._headers["Referer"] = BASE_URL.replace("https://", "")

        self._parser  = _TokenParser()
        self._tokens  = _TokenManager(self._parser)
        self._verify  = verify_tls
        self._client: httpx.AsyncClient | None = None

        # cached security id map  {symbol -> id}
        self._sec_map: dict[str, int] | None = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self):
        self._client = httpx.AsyncClient(verify=self._verify, http2=False, timeout=100)
        return self

    async def __aexit__(self, *_):
        await self._client.aclose()

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _auth_headers_sync(self) -> dict:
        return {
            "Authorization": f"Salter {self._tokens.access_token}",
            "Content-Type":  "application/json",
            **self._headers,
        }

    async def _auth_headers(self) -> dict:
        await self._tokens.get_token(self._client)   # refreshes if needed
        return self._auth_headers_sync()

    async def _get(self, path: str, params: dict | None = None, retry: int = 0) -> any:
        if retry >= MAX_RETRY:
            raise RuntimeError(f"Max retries exceeded: GET {path}")
        try:
            r = await self._client.get(
                f"{BASE_URL}{path}",
                headers=await self._auth_headers(),
                params=params,
            )
            return self._handle(r)
        except (httpx.RemoteProtocolError, httpx.ReadError, httpx.ConnectError):
            return await self._get(path, params, retry + 1)
        except _TokenExpired:
            await self._tokens.update(self._client)
            return await self._get(path, params, retry + 1)

    def _handle(self, resp: httpx.Response) -> any:
        if 200 <= resp.status_code < 300:
            return resp.json()
        if resp.status_code == 401:
            raise _TokenExpired()
        raise RuntimeError(f"NEPSE {resp.status_code}: {resp.text[:200]}")

    # ------------------------------------------------------------------
    # Security ID lookup
    # ------------------------------------------------------------------

    async def _get_sec_map(self) -> dict[str, int]:
        if self._sec_map is None:
            lst = await self._get(self._ep["security_list_url"])
            self._sec_map = {s["symbol"]: s["id"] for s in lst}
        return self._sec_map

    async def _sec_id(self, symbol: str) -> int:
        m = await self._get_sec_map()
        sym = symbol.upper()
        if sym not in m:
            raise ValueError(f"Symbol '{sym}' not found in security list.")
        return m[sym]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_financials_reports(self, symbol: str) -> any:
        """Quarterly/annual financial reports for a company."""
        cid = await self._sec_id(symbol)
        return await self._get(f"{self._ep['Financials_reports']}{cid}/")

    async def get_agm_reports(self, symbol: str) -> any:
        """AGM reports for a company."""
        cid = await self._sec_id(symbol)
        return await self._get(f"{self._ep['Agm_reports']}{cid}/")

    async def get_news_and_alerts(self) -> any:
        """Latest news and market alerts."""
        return await self._get(self._ep["News_Alerts"])

    async def get_corporate_disclosures(self) -> any:
        """Corporate disclosure filings."""
        return await self._get(self._ep["Corporate_Disclosures"])
    
    async def get_corporate_actions(self) -> any:
        """Corporate actions filings."""
        return await self._get(self._ep["Corporate_Actions"])



if __name__ == "__main__":
    asyncio.run(_demo())