from __future__ import annotations

import functools
import logging
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch.Tensor as Tensor
    from transformers.tokenization_utils_tokenizers import TokenizersBackend

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))

model_path = os.path.join(os.environ["MODEL_DIR"], os.environ["MODEL_NAME"])

# `from sentence_transformers import SentenceTransformer` appears to be
# MUCH slower, so load model and tokenizer classes individually
@functools.cache
def get_model() -> Any:
    """Return pretrained model."""
    logger.info(f"Loading model from {model_path}...")
    from transformers import AutoModel
    model = AutoModel.from_pretrained(model_path)
    model.eval()
    logger.info(f"Model loaded.")
    return model

@functools.cache
def get_tokenizer() -> TokenizersBackend:
    """"Return tokenizer based on given model."""
    logger.info(f"Loading tokenizer for {model_path}...")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    logger.info(f"Tokenizer loaded for {model_path}.")
    return tokenizer

def embed_sentences(sentences: list[str], tokenizer: TokenizersBackend, model: Any) -> Tensor:
    """Encode and return sentences submitted, a lower-level, lower-overhead implementation of
    SentenceTransformer encode."""
    import torch
    import torch.nn.functional as F

    encoded = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**encoded)

    # Mean pooling
    token_embeddings = model_output.last_hidden_state
    attention_mask = encoded["attention_mask"]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    pooled = torch.sum(token_embeddings * input_mask_expanded, dim=1) / torch.clamp(
        input_mask_expanded.sum(dim=1), min=1e-9
    )

    return F.normalize(pooled, p=2, dim=1)

def handler(event, context):
    logger.debug(f"Received {event=}.")
    return {
        "embeddings": embed_sentences(event["sentences"], tokenizer=get_tokenizer(), model=get_model()).tolist()
    }
