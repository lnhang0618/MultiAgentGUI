# services/__init__.py
from .mediator_service import MediatorService, DataProvider, CommandHandler

__all__ = [
    'MediatorService',
    'DataProvider',
    'CommandHandler',
]

# 为了向后兼容，保留BackendAdapter和BackendMediator别名
BackendAdapter = MediatorService
BackendMediator = MediatorService
