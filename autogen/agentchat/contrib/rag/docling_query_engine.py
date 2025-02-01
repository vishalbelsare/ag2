# Copyright (c) 2023 - 2025, Owners of https://github.com/ag2ai
#
# SPDX-License-Identifier: Apache-2.0
import hashlib
import logging
import os
import uuid
from typing import Callable, List

from autogen.agentchat.contrib.vectordb.base import Document, QueryResults, VectorDBFactory
from autogen.agentchat.contrib.vectordb.utils import chroma_results_to_query_results, filter_results_by_distance
from autogen.retrieve_utils import query_vector_db, split_files_to_chunks

# Set up logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

HASH_LENGTH = int(os.environ.get("HASH_LENGTH", 8))
DEFAULT_COLLECTION_NAME = "docling-docs"


class DoclingQueryEngine:
    """
    Leverage vectordb to save docling markdown output and query
    """

    def __init__(
        self,
        input_doc_paths: List[str] = None,
        database: str = "chroma",
        collection_name: str = DEFAULT_COLLECTION_NAME,
        overwrite: bool = True,
        embedding_function: Callable = None,
        metadata: dict = None,
        distance_threshold: int = -1,
    ):
        """
        Initializes the DoclingQueryEngine with the specified document paths, database type, and embedding function.
        Args:
            input_doc_paths: The paths to the input documents.
            database: The type of database to use. Defaults to "chroma".
            embedding_function: The embedding function to use. Defaults to None.
            metadata: The metadata of the vector database. Default is None.
        """
        self._overwrite = overwrite
        self._collection_name = collection_name
        self._distance_threshold = distance_threshold
        self._embedding_function = embedding_function
        self._db_config = {"embedding_function": embedding_function, "metadata": metadata}
        self._vector_db = VectorDBFactory.create_vector_db(db_type=database, **self._db_config)

        if not input_doc_paths:
            try:
                self._vector_db.active_collection = self._vector_db.get_collection(self._collection_name)
                logger.warning(
                    f"`input_docs_path` is not provided. Use the existing collection `{self._collection_name}`."
                )
                self._overwrite = False
            except ValueError:
                raise ValueError(
                    "`input_docs_path` is not provided. "
                    f"The collection `{self._collection_name}` doesn't exist either. "
                    "Please provide `docs_path` or create the collection first."
                )

        self._vector_db.active_collection = self._vector_db.create_collection(
            self._collection_name, overwrite=self._overwrite, get_or_create=True
        )

        if input_doc_paths:
            docs = self._chunk_files(input_doc_paths)
            self._vector_db.insert_docs(docs=docs, collection_name=self._collection_name, upsert=True)

    def add_docs(
        self,
        input_doc_paths: List[str] = None,
    ):
        if input_doc_paths:
            docs = self._chunk_files(input_doc_paths)
            self._vector_db.insert_docs(docs=docs, collection_name=self._collection_name, upsert=True)

    def query(self, question: str, n_results=20, search_string: str = None) -> str:
        results = query_vector_db(
            query_texts=[question],
            n_results=n_results,
            search_string=search_string,
            embedding_function=self._embedding_function,
        )
        results["contents"] = results.pop("documents")
        results = chroma_results_to_query_results(results, "distances")
        results = filter_results_by_distance(results, self._distance_threshold)

        answers = self._get_answer(results)

        return answers

    def _chunk_files(self, file_paths: List[str]) -> List[Document]:
        chunks, sources = split_files_to_chunks(files=file_paths)
        logger.info(f"Found {len(chunks)} chunks.")

        chunk_ids = (
            [hashlib.blake2b(chunk.encode("utf-8")).hexdigest()[:HASH_LENGTH] for chunk in chunks]
            if self._vector_db.type != "qdrant"
            else [str(uuid.UUID(hex=hashlib.md5(chunk.encode("utf-8")).hexdigest())) for chunk in chunks]
        )

        chunk_ids_set = set(chunk_ids)
        chunk_ids_set_idx = [chunk_ids.index(hash_value) for hash_value in chunk_ids_set]
        docs = [Document(id=chunk_ids[idx], content=chunks[idx], metadata=sources[idx]) for idx in chunk_ids_set_idx]

        return docs

    def _get_answer(self, results: QueryResults):
        doc_contents = ""

        for idx, doc in enumerate(results[0]):
            doc = doc[0]
            doc_contents += doc["content"] + "\n"

        return doc_contents
