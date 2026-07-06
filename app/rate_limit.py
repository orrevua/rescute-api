"""Shared slowapi limiter (per-client-IP, in-memory) used across routers and main."""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
