"""
market_data.py — serviço de cotações B3, Tesouro Direto e câmbio.

Fontes de dados:
  - B3 (ações, ETFs, FIIs): yfinance (.SA suffix)
  - Tesouro Direto: API pública do Tesouro Nacional
  - PTAX: Banco Central do Brasil (OLINDA API)
  - Câmbio em tempo real: yfinance (par de moedas =X)

Arquitetura:
  MarketDataService
    ├── get_stock(ticker)               → StockQuote
    ├── get_stocks_batch(tickers)       → dict[str, StockQuote]
    ├── get_fii(ticker)                 → FIIQuote
    ├── get_fiis_batch(tickers)         → dict[str, FIIQuote]
    ├── get_tesouro_bonds()             → list[TesouroBond]
    ├── get_ptax(date)                  → ExchangeRate
    ├── get_exchange_rate(pair)         → ExchangeRate
    └── convert(amount, from_, to_)    → float
"""

from __future__ import annotations

import logging
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_EXCEPTION
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from core.circuit_breaker import CircuitOpenError, get_breaker
from core.market_cache import (
    FII_TTL, FX_TTL, PTAX_TTL, STOCK_TTL, TESOURO_TTL, get_cache,
)

log = logging.getLogger(__name__)

_TICKER_RE = re.compile(r"^[A-Z0-9]{4,6}(11|3|4|5|6)?$")


def is_fii(ticker: str) -> bool:
    return bool(ticker) and ticker.endswith("11") and ticker == ticker.upper()


# ── Value objects ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class StockQuote:
    ticker: str
    price: float
    change_pct: float       # variação % no dia
    change_abs: float       # variação em R$
    volume: int
    timestamp: datetime
    source: str = "yfinance"
    is_fallback: bool = False


@dataclass(frozen=True)
class FIIQuote:
    ticker: str
    price: float
    change_pct: float
    change_abs: float
    volume: int
    dy_12m: float           # dividend yield 12 meses (%)
    last_income: float      # último rendimento por cota (R$)
    pvp: float              # preço / valor patrimonial
    timestamp: datetime
    source: str = "yfinance"
    is_fallback: bool = False


@dataclass(frozen=True)
class TesouroBond:
    name: str               # ex: "Tesouro Selic 2029"
    bond_type: str          # LFT, NTN-B, LTN, NTN-F
    rate: float             # taxa anual (%)
    price: float            # preço unitário (R$)
    maturity: date
    min_amount: float = 30.0
    source: str = "tesouro_direto"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ExchangeRate:
    pair: str               # ex: "BRL/USD"
    bid: float              # taxa de compra
    ask: float              # taxa de venda
    mid: float              # ponto médio
    source: str
    timestamp: datetime
    is_fallback: bool = False

    def with_spread(self, spread_pct: float) -> "ExchangeRate":
        """Retorna nova ExchangeRate ajustada pelo spread em %."""
        half = spread_pct / 2 / 100
        return ExchangeRate(
            pair=self.pair,
            bid=round(self.mid * (1 - half), 6),
            ask=round(self.mid * (1 + half), 6),
            mid=self.mid,
            source=self.source,
            timestamp=self.timestamp,
        )


# ── Internal fetch functions ──────────────────────────────────────────────────

def _yf_batch(tickers_sa: list[str]) -> dict[str, dict]:
    """Downloads current-day data for multiple tickers via yfinance in one request."""
    import yfinance as yf

    result: dict[str, dict] = {}
    if not tickers_sa:
        return result

    symbols = " ".join(tickers_sa)
    data = yf.download(
        symbols,
        period="2d",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True,
    )

    import pandas as pd

    # Normalise: single ticker returns flat columns, multi-ticker returns MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        for sym in tickers_sa:
            try:
                df = data[sym].dropna()
                if len(df) < 1:
                    continue
                today = df.iloc[-1]
                prev  = df.iloc[-2] if len(df) >= 2 else today
                close = float(today["Close"])
                prev_close = float(prev["Close"])
                result[sym] = {
                    "price":      close,
                    "change_abs": round(close - prev_close, 4),
                    "change_pct": round((close - prev_close) / prev_close * 100, 4) if prev_close else 0.0,
                    "volume":     int(today.get("Volume", 0) or 0),
                }
            except Exception as e:
                log.debug("_yf_batch: erro para %s: %s", sym, e)
    else:
        # single ticker
        df = data.dropna()
        if len(df) >= 1:
            today = df.iloc[-1]
            prev  = df.iloc[-2] if len(df) >= 2 else today
            close = float(today["Close"])
            prev_close = float(prev["Close"])
            sym = tickers_sa[0]
            result[sym] = {
                "price":      close,
                "change_abs": round(close - prev_close, 4),
                "change_pct": round((close - prev_close) / prev_close * 100, 4) if prev_close else 0.0,
                "volume":     int(today.get("Volume", 0) or 0),
            }

    return result


def _fetch_tesouro_raw() -> list[dict]:
    """Fetches Tesouro Direto bonds from official API."""
    import httpx

    url = (
        "https://www.tesourodireto.com.br/json/br/com/b3/"
        "tesourodireto/service/api/treasurybondsfile.json"
    )
    resp = httpx.get(url, timeout=10.0, follow_redirects=True)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("response", {}).get("TrsrBdTradgList", [])


def _fetch_ptax_raw(ptax_date: str) -> dict:
    """Fetches PTAX (BRL/USD) closing rate from Banco Central OLINDA API."""
    import httpx

    url = (
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
        f"CotacaoDolarDia(dataCotacao=@dataCotacao)"
        f"?@dataCotacao='{ptax_date}'"
        "&$top=1&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"
    )
    resp = httpx.get(url, timeout=10.0)
    resp.raise_for_status()
    data = resp.json().get("value", [])
    if not data:
        raise ValueError(f"PTAX não disponível para {ptax_date}")
    return data[0]


def _fetch_fx_raw(yf_symbol: str) -> dict:
    """Fetches real-time exchange rate via yfinance (e.g. 'BRL=X', 'BRLUSD=X')."""
    import yfinance as yf

    ticker = yf.Ticker(yf_symbol)
    info = ticker.fast_info
    price = float(info.last_price or 0)
    prev  = float(info.previous_close or price)
    return {
        "price":      price,
        "change_abs": round(price - prev, 6),
        "change_pct": round((price - prev) / prev * 100, 4) if prev else 0.0,
    }


# ── Parse helpers ─────────────────────────────────────────────────────────────

def _parse_bond_type(name: str) -> str:
    mapping = {
        "Selic":      "LFT",
        "IPCA":       "NTN-B",
        "Prefixado":  "LTN",
        "Renda+":     "NTN-B Renda+",
        "RendA+":     "NTN-B Renda+",
        "Educa+":     "NTN-B Educa+",
    }
    for keyword, code in mapping.items():
        if keyword.lower() in name.lower():
            return code
    return "OUTRO"


def _parse_tesouro_bond(raw: dict) -> TesouroBond | None:
    try:
        bond = raw.get("TrsrBd", {})
        name = bond.get("nm", "")
        rate_str = bond.get("anulInvstmtRate", 0)
        price_str = bond.get("untrInvstmtVal", 0)
        maturity_str = bond.get("mtrtyDt", "")
        min_str = bond.get("minInvstmtAmt", 30)
        maturity = datetime.strptime(maturity_str[:10], "%Y-%m-%d").date()
        return TesouroBond(
            name=name,
            bond_type=_parse_bond_type(name),
            rate=round(float(rate_str), 4),
            price=round(float(price_str), 2),
            maturity=maturity,
            min_amount=round(float(min_str), 2),
            timestamp=datetime.now(),
        )
    except Exception as e:
        log.debug("_parse_tesouro_bond falhou: %s | raw=%s", e, raw)
        return None


# ── MarketDataService ─────────────────────────────────────────────────────────

class MarketDataService:
    """
    Serviço de cotações B3, Tesouro e câmbio com cache + circuit breaker.

    Usage:
        svc = MarketDataService()
        q   = svc.get_stock("PETR4")
        qs  = svc.get_stocks_batch(["PETR4", "VALE3", "ITUB4"])
        fii = svc.get_fii("MXRF11")
        bonds = svc.get_tesouro_bonds()
        ptax = svc.get_ptax()
        rate = svc.get_exchange_rate("BRL/USD")
        brl  = svc.convert(100, "USD", "BRL")
    """

    # yfinance symbol suffix for pairs
    _FX_MAP: dict[str, str] = {
        "BRL/USD": "BRLUSD=X",
        "USD/BRL": "BRL=X",
        "EUR/BRL": "EURBRL=X",
        "BRL/EUR": "BRLUSD=X",   # approximate via USD route
        "USD/EUR": "USDEUR=X",
    }

    def __init__(
        self,
        cache=None,
        batch_size: int = 100,
        max_workers: int = 8,
    ) -> None:
        self._cache = cache or get_cache()
        self._batch_size = batch_size
        self._max_workers = max_workers
        self._cb_yf     = get_breaker("yfinance",     failure_threshold=5, recovery_timeout=60)
        self._cb_tesouro = get_breaker("tesouro",     failure_threshold=3, recovery_timeout=120)
        self._cb_bcb    = get_breaker("bcb_ptax",     failure_threshold=3, recovery_timeout=120)

    # ── B3 Stocks / ETFs ─────────────────────────────────────────────────────

    def get_stock(self, ticker: str, force_refresh: bool = False) -> StockQuote | None:
        """Retorna cotação de uma ação ou ETF da B3."""
        ticker = ticker.upper().strip()
        key = f"stock:{ticker}"

        if not force_refresh:
            cached = self._cache.get(key)
            if cached:
                return self._dict_to_stock(cached, ticker)

        try:
            data = self._cb_yf.call(_yf_batch, [f"{ticker}.SA"])
            raw = data.get(f"{ticker}.SA")
            if not raw:
                return self._stock_from_fallback(key, ticker)
            quote = self._make_stock(ticker, raw)
            self._cache.set(key, self._stock_to_dict(quote), STOCK_TTL)
            return quote
        except CircuitOpenError:
            log.warning("get_stock(%s): circuito aberto — usando fallback", ticker)
        except Exception as e:
            log.warning("get_stock(%s) falhou: %s", ticker, e)
        return self._stock_from_fallback(key, ticker)

    def get_stocks_batch(
        self,
        tickers: list[str],
        force_refresh: bool = False,
    ) -> dict[str, StockQuote]:
        """
        Retorna cotações de múltiplos ativos B3 em paralelo.
        Divide em lotes de self._batch_size por request ao yfinance.
        """
        tickers = [t.upper().strip() for t in tickers]
        result: dict[str, StockQuote] = {}
        missing: list[str] = []

        # 1. Servir do cache
        if not force_refresh:
            for ticker in tickers:
                cached = self._cache.get(f"stock:{ticker}")
                if cached:
                    result[ticker] = self._dict_to_stock(cached, ticker)
                else:
                    missing.append(ticker)
        else:
            missing = list(tickers)

        if not missing:
            return result

        # 2. Buscar em lotes
        batches = [
            missing[i : i + self._batch_size]
            for i in range(0, len(missing), self._batch_size)
        ]

        def _fetch_batch(batch: list[str]) -> dict[str, Any]:
            sa_tickers = [f"{t}.SA" for t in batch]
            return self._cb_yf.call(_yf_batch, sa_tickers)

        try:
            with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
                futures = {pool.submit(_fetch_batch, b): b for b in batches}
                for future in as_completed(futures):
                    batch = futures[future]
                    try:
                        data = future.result()
                        for ticker in batch:
                            raw = data.get(f"{ticker}.SA")
                            if raw:
                                q = self._make_stock(ticker, raw)
                                self._cache.set(f"stock:{ticker}", self._stock_to_dict(q), STOCK_TTL)
                                result[ticker] = q
                            else:
                                fb = self._stock_from_fallback(f"stock:{ticker}", ticker)
                                if fb:
                                    result[ticker] = fb
                    except CircuitOpenError:
                        for ticker in batch:
                            fb = self._stock_from_fallback(f"stock:{ticker}", ticker)
                            if fb:
                                result[ticker] = fb
                    except Exception as e:
                        log.warning("batch fetch falhou (%s): %s", batch[:3], e)
        except Exception as e:
            log.error("get_stocks_batch: erro geral: %s", e)

        return result

    # ── FIIs ─────────────────────────────────────────────────────────────────

    def get_fii(self, ticker: str, force_refresh: bool = False) -> FIIQuote | None:
        """
        Retorna cotação de FII com métricas fundamentais.
        Preço/variação via yfinance; DY/PVP via yfinance info (aproximado).
        """
        ticker = ticker.upper().strip()
        key = f"fii:{ticker}"

        if not force_refresh:
            cached = self._cache.get(key)
            if cached:
                return self._dict_to_fii(cached, ticker)

        try:
            import yfinance as yf

            def _fetch_fii_full(t: str) -> dict:
                sym = f"{t}.SA"
                yft = yf.Ticker(sym)
                info = yft.info or {}
                fast = yft.fast_info

                price     = float(fast.last_price or 0)
                prev      = float(fast.previous_close or price)
                bvps      = float(info.get("bookValue", 0) or 0)
                dy_dec    = float(info.get("trailingAnnualDividendYield", 0) or 0)
                div_rate  = float(info.get("trailingAnnualDividendRate", 0) or 0)

                return {
                    "price":       price,
                    "change_abs":  round(price - prev, 4),
                    "change_pct":  round((price - prev) / prev * 100, 4) if prev else 0.0,
                    "volume":      int(fast.three_month_average_volume or 0),
                    "dy_12m":      round(dy_dec * 100, 4),
                    "last_income": round(div_rate / 12, 4) if div_rate else 0.0,
                    "pvp":         round(price / bvps, 4) if bvps else 0.0,
                }

            raw = self._cb_yf.call(_fetch_fii_full, ticker)
            quote = FIIQuote(
                ticker=ticker,
                price=raw["price"],
                change_pct=raw["change_pct"],
                change_abs=raw["change_abs"],
                volume=raw["volume"],
                dy_12m=raw["dy_12m"],
                last_income=raw["last_income"],
                pvp=raw["pvp"],
                timestamp=datetime.now(),
            )
            self._cache.set(key, self._fii_to_dict(quote), FII_TTL)
            return quote

        except CircuitOpenError:
            log.warning("get_fii(%s): circuito aberto", ticker)
        except Exception as e:
            log.warning("get_fii(%s) falhou: %s", ticker, e)

        return self._fii_from_fallback(key, ticker)

    def get_fiis_batch(
        self,
        tickers: list[str],
        force_refresh: bool = False,
    ) -> dict[str, FIIQuote]:
        """Busca FIIs em paralelo (mesma lógica do batch de ações)."""
        tickers = [t.upper().strip() for t in tickers]
        result: dict[str, FIIQuote] = {}
        missing: list[str] = []

        if not force_refresh:
            for t in tickers:
                cached = self._cache.get(f"fii:{t}")
                if cached:
                    result[t] = self._dict_to_fii(cached, t)
                else:
                    missing.append(t)
        else:
            missing = list(tickers)

        with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
            futures = {pool.submit(self.get_fii, t, force_refresh): t for t in missing}
            for fut in as_completed(futures):
                t = futures[fut]
                try:
                    q = fut.result()
                    if q:
                        result[t] = q
                except Exception as e:
                    log.debug("get_fiis_batch: %s falhou: %s", t, e)

        return result

    def get_price_history(
        self,
        tickers: list[str],
        days: int = 30,
        force_refresh: bool = False,
    ) -> dict[str, list[dict]]:
        """Retorna histórico de preços de fechamento para os últimos `days` dias.

        Returns:
            {ticker: [{"date": date, "close": float}, ...]} ordenado cronologicamente.
        """
        if not tickers:
            return {}

        sa_tickers = [f"{t}.SA" for t in tickers]
        try:
            import yfinance as yf
            df = yf.download(sa_tickers, period=f"{days}d", interval="1d", progress=False, auto_adjust=True)
        except Exception as e:
            log.debug("get_price_history: yfinance falhou: %s", e)
            return {}

        if df is None or df.empty:
            return {}

        result: dict[str, list[dict]] = {}
        for ticker, sa in zip(tickers, sa_tickers):
            try:
                if ("Close", sa) in df.columns:
                    series = df[("Close", sa)].dropna()
                elif "Close" in df.columns:
                    series = df["Close"].dropna()
                else:
                    continue
                entries = [
                    {"date": idx.date(), "close": float(val)}
                    for idx, val in series.items()
                ]
                entries.sort(key=lambda e: e["date"])
                if entries:
                    result[ticker] = entries
            except Exception as e:
                log.debug("get_price_history: parse de %s falhou: %s", ticker, e)

        return result

    # ── Tesouro Direto ────────────────────────────────────────────────────────

    def get_tesouro_bonds(self, force_refresh: bool = False) -> list[TesouroBond]:
        """Retorna todos os títulos do Tesouro Direto disponíveis para compra."""
        key = "tesouro:bonds"

        if not force_refresh:
            cached = self._cache.get(key)
            if cached:
                return [TesouroBond(**b) for b in cached]

        try:
            raw_list = self._cb_tesouro.call(_fetch_tesouro_raw)
            bonds = [b for r in raw_list if (b := _parse_tesouro_bond(r)) is not None]
            if bonds:
                self._cache.set(key, [self._bond_to_dict(b) for b in bonds], TESOURO_TTL)
                return bonds
        except CircuitOpenError:
            log.warning("get_tesouro_bonds: circuito aberto")
        except Exception as e:
            log.warning("get_tesouro_bonds falhou: %s", e)

        fallback = self._cache.get_fallback(key)
        if fallback:
            return [TesouroBond(**b) for b in fallback]
        return []

    _TESOURO_CSV_URL = (
        "https://www.tesourodireto.com.br/json/br/com/b3/tesouro/"
        "tesouro-direto/1/TesouroDireto_HistoricoTaxaPreco.csv"
    )

    def get_tesouro_history(
        self,
        bond_type: str | None = None,
        start_date: date | None = None,
    ) -> list[dict]:
        """Retorna histórico de preços e taxas do Tesouro Direto via CSV público.

        Returns:
            [{"date": date, "bond_type": str, "rate_buy": float,
              "rate_sell": float, "price_buy": float}, ...]
            ordenado cronologicamente.
        """
        import io
        import requests
        import pandas as pd

        try:
            resp = requests.get(self._TESOURO_CSV_URL, timeout=15)
            resp.raise_for_status()
            df = pd.read_csv(
                io.BytesIO(resp.content),
                sep=";",
                encoding="latin-1",
                decimal=",",
                thousands=".",
            )
        except Exception as e:
            log.debug("get_tesouro_history: falhou ao buscar CSV: %s", e)
            return []

        # Normaliza nomes de colunas (remove espaços extras)
        df.columns = [c.strip() for c in df.columns]

        # Mapeia para nomes canônicos — colunas variam ligeiramente entre versões do CSV
        col_map = {
            "Tipo Título": "bond_type",
            "Tipo T\xedtulo": "bond_type",
            "Data Venda": "date_str",
            "Taxa Compra Manha": "rate_buy",
            "Taxa Compra Manh\xe3": "rate_buy",
            "Taxa Venda Manha": "rate_sell",
            "Taxa Venda Manh\xe3": "rate_sell",
            "PU Compra Manha": "price_buy",
            "PU Compra Manh\xe3": "price_buy",
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        required = {"bond_type", "date_str", "rate_buy", "price_buy"}
        if not required.issubset(df.columns):
            log.debug("get_tesouro_history: colunas esperadas não encontradas: %s", df.columns.tolist())
            return []

        if bond_type:
            df = df[df["bond_type"] == bond_type]

        result = []
        for _, row in df.iterrows():
            try:
                d = datetime.strptime(str(row["date_str"]).strip(), "%d/%m/%Y").date()
                if start_date and d < start_date:
                    continue
                result.append({
                    "date": d,
                    "bond_type": str(row["bond_type"]).strip(),
                    "rate_buy": float(row["rate_buy"]),
                    "rate_sell": float(row.get("rate_sell", row["rate_buy"])),
                    "price_buy": float(row["price_buy"]),
                })
            except Exception:
                continue

        result.sort(key=lambda r: r["date"])
        return result

    # ── Câmbio ────────────────────────────────────────────────────────────────

    def get_ptax(
        self,
        reference_date: date | None = None,
        force_refresh: bool = False,
    ) -> ExchangeRate | None:
        """
        Retorna a PTAX (BRL/USD) do fechamento do Banco Central.
        Usa a data de referência informada, ou o dia útil anterior.
        """
        ref = reference_date or self._last_business_day()
        ptax_str = ref.strftime("%m-%d-%Y")  # formato BCB: MM-DD-YYYY
        key = f"ptax:{ref.isoformat()}"

        if not force_refresh:
            cached = self._cache.get(key)
            if cached:
                return ExchangeRate(**cached)

        try:
            raw = self._cb_bcb.call(_fetch_ptax_raw, ptax_str)
            bid = float(raw["cotacaoCompra"])
            ask = float(raw["cotacaoVenda"])
            rate = ExchangeRate(
                pair="BRL/USD",
                bid=round(bid, 6),
                ask=round(ask, 6),
                mid=round((bid + ask) / 2, 6),
                source="bcb_ptax",
                timestamp=datetime.now(),
            )
            self._cache.set(key, self._rate_to_dict(rate), PTAX_TTL)
            return rate
        except CircuitOpenError:
            log.warning("get_ptax: circuito aberto")
        except Exception as e:
            log.warning("get_ptax(%s) falhou: %s", ptax_str, e)

        fallback = self._cache.get_fallback(key)
        if fallback:
            return ExchangeRate(**{**fallback, "is_fallback": True})
        return None

    def get_exchange_rate(
        self,
        pair: str = "BRL/USD",
        spread_pct: float = 0.0,
        force_refresh: bool = False,
    ) -> ExchangeRate | None:
        """
        Retorna cotação de câmbio em tempo real via yfinance.
        pair: "BRL/USD" | "USD/BRL" | "EUR/BRL" | "BRL/EUR" | "USD/EUR"
        spread_pct: spread configurável adicionado ao mid.
        """
        pair = pair.upper()
        yf_sym = self._FX_MAP.get(pair)
        if not yf_sym:
            raise ValueError(f"Par de moedas não suportado: {pair}. Use: {list(self._FX_MAP)}")

        key = f"fx:{pair}"

        if not force_refresh:
            cached = self._cache.get(key)
            if cached:
                rate = ExchangeRate(**cached)
                return rate.with_spread(spread_pct) if spread_pct else rate

        try:
            raw = self._cb_yf.call(_fetch_fx_raw, yf_sym)
            price = raw["price"]
            rate = ExchangeRate(
                pair=pair,
                bid=price,
                ask=price,
                mid=price,
                source="yfinance",
                timestamp=datetime.now(),
            )
            self._cache.set(key, self._rate_to_dict(rate), FX_TTL)
            result = rate.with_spread(spread_pct) if spread_pct else rate
            return result
        except CircuitOpenError:
            log.warning("get_exchange_rate(%s): circuito aberto", pair)
        except Exception as e:
            log.warning("get_exchange_rate(%s) falhou: %s", pair, e)

        fallback = self._cache.get_fallback(key)
        if fallback:
            rate = ExchangeRate(**{**fallback, "is_fallback": True})
            return rate.with_spread(spread_pct) if spread_pct else rate
        return None

    def convert(
        self,
        amount: float,
        from_ccy: str,
        to_ccy: str,
        spread_pct: float = 0.0,
        use_ask: bool = True,
    ) -> float | None:
        """
        Converte amount de from_ccy para to_ccy.
        use_ask=True → usa taxa de venda (compra de moeda estrangeira).
        Retorna None se câmbio indisponível.
        """
        if from_ccy == to_ccy:
            return round(amount, 2)

        pair = f"{from_ccy}/{to_ccy}"
        alt_pair = f"{to_ccy}/{from_ccy}"

        rate = self.get_exchange_rate(pair, spread_pct=spread_pct)
        if rate:
            price = rate.ask if use_ask else rate.bid
            return round(amount * price, 2)

        # tenta par inverso
        rate = self.get_exchange_rate(alt_pair, spread_pct=spread_pct)
        if rate:
            price = rate.bid if use_ask else rate.ask
            return round(amount / price, 2) if price else None

        return None

    # ── Fallback helpers ──────────────────────────────────────────────────────

    def _stock_from_fallback(self, key: str, ticker: str) -> StockQuote | None:
        data = self._cache.get_fallback(key)
        if data:
            q = self._dict_to_stock(data, ticker)
            return StockQuote(**{**self._stock_to_dict(q), "is_fallback": True, "ticker": ticker})
        return None

    def _fii_from_fallback(self, key: str, ticker: str) -> FIIQuote | None:
        data = self._cache.get_fallback(key)
        if data:
            q = self._dict_to_fii(data, ticker)
            return FIIQuote(**{**self._fii_to_dict(q), "is_fallback": True, "ticker": ticker})
        return None

    # ── Serialisation helpers ─────────────────────────────────────────────────

    @staticmethod
    def _make_stock(ticker: str, raw: dict) -> StockQuote:
        return StockQuote(
            ticker=ticker,
            price=raw["price"],
            change_pct=raw["change_pct"],
            change_abs=raw["change_abs"],
            volume=raw["volume"],
            timestamp=datetime.now(),
        )

    @staticmethod
    def _stock_to_dict(q: StockQuote) -> dict:
        return {
            "ticker": q.ticker, "price": q.price,
            "change_pct": q.change_pct, "change_abs": q.change_abs,
            "volume": q.volume, "timestamp": q.timestamp.isoformat(),
            "source": q.source, "is_fallback": q.is_fallback,
        }

    @staticmethod
    def _dict_to_stock(d: dict, ticker: str) -> StockQuote:
        return StockQuote(
            ticker=ticker, price=d["price"],
            change_pct=d["change_pct"], change_abs=d["change_abs"],
            volume=d["volume"],
            timestamp=datetime.fromisoformat(d["timestamp"]) if isinstance(d["timestamp"], str) else d["timestamp"],
            source=d.get("source", "cache"),
            is_fallback=d.get("is_fallback", False),
        )

    @staticmethod
    def _fii_to_dict(q: FIIQuote) -> dict:
        return {
            "ticker": q.ticker, "price": q.price,
            "change_pct": q.change_pct, "change_abs": q.change_abs,
            "volume": q.volume, "dy_12m": q.dy_12m,
            "last_income": q.last_income, "pvp": q.pvp,
            "timestamp": q.timestamp.isoformat(),
            "source": q.source, "is_fallback": q.is_fallback,
        }

    @staticmethod
    def _dict_to_fii(d: dict, ticker: str) -> FIIQuote:
        return FIIQuote(
            ticker=ticker, price=d["price"],
            change_pct=d["change_pct"], change_abs=d["change_abs"],
            volume=d["volume"], dy_12m=d["dy_12m"],
            last_income=d["last_income"], pvp=d["pvp"],
            timestamp=datetime.fromisoformat(d["timestamp"]) if isinstance(d["timestamp"], str) else d["timestamp"],
            source=d.get("source", "cache"),
            is_fallback=d.get("is_fallback", False),
        )

    @staticmethod
    def _bond_to_dict(b: TesouroBond) -> dict:
        return {
            "name": b.name, "bond_type": b.bond_type,
            "rate": b.rate, "price": b.price,
            "maturity": b.maturity.isoformat(),
            "min_amount": b.min_amount, "source": b.source,
            "timestamp": b.timestamp.isoformat(),
        }

    @staticmethod
    def _rate_to_dict(r: ExchangeRate) -> dict:
        return {
            "pair": r.pair, "bid": r.bid, "ask": r.ask, "mid": r.mid,
            "source": r.source, "timestamp": r.timestamp.isoformat(),
            "is_fallback": r.is_fallback,
        }

    @staticmethod
    def _last_business_day() -> date:
        """Retorna o último dia útil (exclui sábado e domingo)."""
        from datetime import timedelta
        d = date.today()
        # Se hoje é segunda (0) ou terça-domingo vai para sexta ou ontem
        step = 1
        if d.weekday() == 0:   # segunda → sexta
            step = 3
        elif d.weekday() == 6: # domingo → sexta
            step = 2
        return d - timedelta(days=step)


# Singleton de conveniência
_service: MarketDataService | None = None
_service_lock = threading.Lock()


def get_market_service(cache=None) -> MarketDataService:
    global _service
    with _service_lock:
        if _service is None or cache is not None:
            _service = MarketDataService(cache=cache)
    return _service
