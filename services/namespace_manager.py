class NamespaceManager:
    def __init__(self):
        self._namespaces: list[str] = []

    def add(self, namespace: str) -> None:
        if namespace not in self._namespaces:
            self._namespaces.append(namespace)

    def all(self) -> list[str]:
        return self._namespaces.copy()

    def clear(self) -> None:
        self._namespaces.clear()