import logging
import os
import time
import torch

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
logger.info(torch.__version__)
logger.info('cuda?')
logger.info(torch.cuda.is_available())


logger.info("Loading AutoTokenizer...")
from transformers import AutoTokenizer
logger.info("AutoTokenizer loaded.")

logger.info("Loading AutoModel...")
from transformers import AutoModel
logger.info("AutoModel loaded.")

MINI_LM_PATH = os.path.join(os.environ["MODEL_DIR"], "all-MiniLM-L6-v2")

start = time.time()
logger.info("Loading all-MiniLM-L6-v2...")
_tokenizer = AutoTokenizer.from_pretrained(MINI_LM_PATH)
_model = AutoModel.from_pretrained(MINI_LM_PATH)
_model.eval()
logger.info(f"all-MiniLM-L6-v2 loaded in {time.time() - start:.2f}s")

def handler(event, context):
    pass