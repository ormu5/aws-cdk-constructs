from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING

# import torch

if TYPE_CHECKING:
    import torch.Tensor as Tensor

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
# logger.info(torch.__version__)
# logger.info('cuda?')
# logger.info(torch.cuda.is_available())

MINI_LM_PATH = os.path.join(os.environ["MODEL_DIR"], "all-MiniLM-L6-v2")

start = time.time()
logger.info("Loading all-MiniLM-L6-v2...")
# _tokenizer = AutoTokenizer.from_pretrained(MINI_LM_PATH)
# _model = AutoModel.from_pretrained(MINI_LM_PATH)
# _model.eval()
logger.info(f"all-MiniLM-L6-v2 loaded in {time.time() - start:.2f}s")

def handler(event, context):
    # logger.info("Loading AutoModel...")
    # from transformers import AutoModel
    # logger.info("AutoModel loaded.")
    #
    # logger.info("Loading AutoTokenizer...")
    # from transformers import AutoTokenizer
    # logger.info("AutoTokenizer loaded.")
    logger.info("Loading SentenceTransformer...")
    from sentence_transformers import SentenceTransformer
    logger.info("SentenceTransformer loaded.")


# # Tokenizer and model initialized during handler execution, and cached.
# _tokenizer = None
# _model = None
#
#
# def embed_sentences(sentences, tokenizer, model) -> Tensor:
#     """Encode and return sentences submitted, a lower-level, lower-overhead implementation of
#     SentenceTransformer encode to facilitate cold start loading in Lambda."""
    # import torch
    # import torch.nn.functional as F
    #
    # sentences = [s.lower() for s in sentences]
    # encoded = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
    # with torch.no_grad():
    #     model_output = model(**encoded)
    #
    # # Mean pooling
    # token_embeddings = model_output.last_hidden_state
    # attention_mask = encoded["attention_mask"]
    # input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    # pooled = torch.sum(token_embeddings * input_mask_expanded, dim=1) / torch.clamp(
    #     input_mask_expanded.sum(dim=1), min=1e-9
    # )
    #
    # return F.normalize(pooled, p=2, dim=1)


# @event_source(data_class=APIGatewayProxyEvent)
# def handler(event: APIGatewayProxyEvent, context):
#     """Infers route type from hauling sites, service descriptions, and [OCSD] waste types
#     submitted in request payload. Multiple values can be submitted for each - although
#     all must have the same number of values - and a response with corresponding values
#     will be returned.
#
#     E.g., a POST payload of
#         {
#             "hauling_sites": ["S06540", "S03774"],
#             "service_descriptions": ["8 yd rel", "4 yd rel"],
#             "waste_types": ["MSW", "MSW"]
#         }
#     might return a value of ["RC", "RC"]
#     """
#     global _tokenizer, _model
#     if _tokenizer is None or _model is None:  # Load and cache
#         start = time.time()
#         from transformers import AutoTokenizer, AutoModel
#
#         logger.info("Loading all-MiniLM-L6-v2...")
#         _tokenizer = AutoTokenizer.from_pretrained(MINI_LM_PATH)
#         _model = AutoModel.from_pretrained(MINI_LM_PATH)
#         _model.eval()
#         logger.info(f"all-MiniLM-L6-v2 loaded in {time.time() - start:.2f}s")
#
#     event_json = event.json_body
#     hauling_sites = event_json["hauling_sites"]
#     service_descriptions = event_json["service_descriptions"]
#     waste_types = event_json["waste_types"]
#     logger.info(f"Received {hauling_sites}, {service_descriptions}, {waste_types}")
#     if not (len(hauling_sites) == len(service_descriptions) == len(waste_types)):
#         return log_and_respond(
#             http_status=HTTPStatusEnum.NOT_ACCEPTABLE,
#             reference_id=event.request_context.request_id,
#             body={
#                 "message": "Different length input arguments specified. Please specify arguments of same length"
#             },
#         )
#
#     input_hs = embed_sentences(hauling_sites, _tokenizer, _model)
#     input_svc_desc = embed_sentences(service_descriptions, _tokenizer, _model)
#     input_waste_type = waste_ohe_model.transform(
#         np.array([wt.lower() for wt in waste_types]).reshape(-1, 1)
#     )
#     input_x = np.hstack([input_hs, input_svc_desc, input_waste_type])
#     logger.info(f"Calling predict on classifier for inputs with shape {input_x.shape}.")
#     y_pred = classifier.predict(input_x)
#     class_indices = np.argmax(y_pred, axis=1)
#     class_labels = route_ohe_model.categories_[0]
#     ml_route_type_results = [class_labels[i] for i in class_indices]
#
#     return log_and_respond(
#         http_status=HTTPStatusEnum.OK,
#         reference_id=event.request_context.request_id,
#         body=ml_route_type_results,
#     )
