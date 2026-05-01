# Copyright [2026] Ziffan (Ziffany Firdinal)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers import util as st_util

    _AVAILABLE = True
except ImportError:
    pass

_model = None
MODEL_NAME = "intfloat/multilingual-e5-large"
_INSTALL_MSG = (
    "Retrieval feature requires extras. "
    "Install: pip install -r requirements-retrieval.txt"
)

# multilingual-e5 requires explicit role prefixes for asymmetric retrieval.
_QUERY_PREFIX = "query: "
_PASSAGE_PREFIX = "passage: "


def is_available() -> bool:
    return _AVAILABLE


def _get_model():
    global _model
    if not _AVAILABLE:
        raise ImportError(_INSTALL_MSG)
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def retrieve(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    """Return top-K chunks ranked by cosine similarity to query."""
    model = _get_model()
    if not chunks:
        return []
    texts = [_PASSAGE_PREFIX + c["text"] for c in chunks]
    query_emb = model.encode(_QUERY_PREFIX + query, convert_to_tensor=True)
    chunk_embs = model.encode(texts, convert_to_tensor=True)
    scores = st_util.cos_sim(query_emb, chunk_embs)[0].tolist()
    ranked = sorted(
        [
            {"index": c["index"], "score": round(float(s), 6), "text": c["text"]}
            for c, s in zip(chunks, scores)
        ],
        key=lambda x: x["score"],
        reverse=True,
    )
    return ranked[:top_k]
