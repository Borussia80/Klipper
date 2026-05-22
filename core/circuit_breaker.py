"""Circuit breaker para APIs de cotação instáveis."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from enum import Enum
from time import monotonic
from typing import Callable, TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")


class _State(str, Enum):
    CLOSED    = "closed"     # operação normal
    OPEN      = "open"       # bloqueado após N falhas
    HALF_OPEN = "half_open"  # testando recuperação


@dataclass
class CircuitBreaker:
    """
    Implementação thread-safe do padrão Circuit Breaker.

    Estados:
      CLOSED    → chamadas passam normalmente; conta falhas.
      OPEN      → chamadas bloqueadas até recovery_timeout expirar.
      HALF_OPEN → uma chamada de teste; sucesso → CLOSED, falha → OPEN.
    """
    name: str
    failure_threshold: int = 5
    recovery_timeout: float = 60.0   # segundos

    _state: _State = field(default=_State.CLOSED, init=False, repr=False)
    _failures: int = field(default=0, init=False, repr=False)
    _opened_at: float = field(default=0.0, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    @property
    def state(self) -> _State:
        with self._lock:
            return self._current_state()

    def _current_state(self) -> _State:
        if self._state == _State.OPEN:
            if monotonic() - self._opened_at >= self.recovery_timeout:
                self._state = _State.HALF_OPEN
                log.info("CircuitBreaker[%s] → HALF_OPEN", self.name)
        return self._state

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Executa func(*args, **kwargs) respeitando o estado do circuit breaker.
        Levanta CircuitOpenError se o circuito está OPEN.
        """
        with self._lock:
            state = self._current_state()

        if state == _State.OPEN:
            raise CircuitOpenError(self.name)

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except CircuitOpenError:
            raise
        except Exception as exc:
            self._on_failure(exc)
            raise

    def _on_success(self) -> None:
        with self._lock:
            if self._state == _State.HALF_OPEN:
                log.info("CircuitBreaker[%s] → CLOSED (recuperado)", self.name)
            self._state = _State.CLOSED
            self._failures = 0

    def _on_failure(self, exc: Exception) -> None:
        with self._lock:
            self._failures += 1
            log.warning(
                "CircuitBreaker[%s] falha %d/%d: %s",
                self.name, self._failures, self.failure_threshold, exc,
            )
            if self._failures >= self.failure_threshold or self._state == _State.HALF_OPEN:
                self._state = _State.OPEN
                self._opened_at = monotonic()
                log.error(
                    "CircuitBreaker[%s] → OPEN (bloqueado por %.0fs)",
                    self.name, self.recovery_timeout,
                )

    def reset(self) -> None:
        """Força o circuito de volta ao estado CLOSED (para testes/admin)."""
        with self._lock:
            self._state = _State.CLOSED
            self._failures = 0
            self._opened_at = 0.0


class CircuitOpenError(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Circuit breaker '{name}' está OPEN — API indisponível.")
        self.circuit_name = name


# Registro global: uma instância por fonte de dados
_registry: dict[str, CircuitBreaker] = {}
_registry_lock = threading.Lock()


def get_breaker(name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0) -> CircuitBreaker:
    """Retorna (ou cria) o circuit breaker para a fonte de dados informada."""
    with _registry_lock:
        if name not in _registry:
            _registry[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )
        return _registry[name]
