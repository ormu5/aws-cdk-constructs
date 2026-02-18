from constructs import Construct


class VectorIndexWriteLambda(Construct):
    """Given structured data, converts to semantic text based on config,
    performs embedding, and submits embedding and metadata to vector store
    at the given index."""
    def __init__(
            self, scope: Construct, *,
            name: str,
            **kwargs
    ) -> None:
        stack_id = "-".join([name, "stack"])
        super().__init__(scope, stack_id, **kwargs)