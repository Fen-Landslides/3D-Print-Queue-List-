import os
from repositories.local_repository import LocalRepository
from repositories.firestore_repository import FirestoreRepository


def create_repository():
    backend = os.environ.get("STORAGE_BACKEND", "local").lower()
    queue_id = os.environ.get("FIRESTORE_QUEUE_ID", "default")
    if backend == "firestore":
        return FirestoreRepository(queue_id=queue_id)
    return LocalRepository()
