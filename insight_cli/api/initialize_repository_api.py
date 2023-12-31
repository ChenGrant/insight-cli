from concurrent.futures import ThreadPoolExecutor
import copy, requests, secrets

from .base.api import API
from insight_cli import config


class InitializeRepositoryAPI(API):
    @staticmethod
    def _generate_request_session_id() -> str:
        return secrets.token_hex()

    @staticmethod
    def _get_batched_repository_files(
        repository_files: dict[str, bytes]
    ) -> list[dict[str, dict[str, bytes]]]:
        MAX_BATCH_SIZE_BYTES = 10 * 1024**2

        batches = []
        empty_batch = {"files": {}}
        current_batch = copy.deepcopy(empty_batch)
        current_batch_size_bytes = 0

        for file_path, file_content in repository_files.items():
            file_size_bytes = len(file_content)

            current_batch["files"][file_path] = file_content
            current_batch_size_bytes += file_size_bytes

            if current_batch_size_bytes + file_size_bytes > MAX_BATCH_SIZE_BYTES:
                batches.append(current_batch)
                current_batch = copy.deepcopy(empty_batch)
                current_batch_size_bytes = 0

        if current_batch != empty_batch:
            batches.append(current_batch)

        return batches

    @classmethod
    def _add_batches_request_metadata(
        cls, batches: list[dict[str, dict[str, bytes]]]
    ) -> list[dict[str, dict[str, bytes] | int | str]]:
        session_id = cls._generate_request_session_id()

        for i, batch in enumerate(batches):
            batch.update(
                {
                    "batch_number": i + 1,
                    "num_total_batches": len(batches),
                    "session_id": session_id,
                }
            )

        return batches

    @staticmethod
    def _make_batch_request(
        payload: dict[str, dict[str, bytes] | int | str]
    ) -> dict[str, str]:
        response = requests.post(
            url=f"{config.INSIGHT_API_BASE_URL}/initialize_repository",
            cookies={"session_id": payload["session_id"]},
            files=payload["files"],
            data={
                "batch_num": payload["batch_number"],
                "num_total_batches": payload["num_total_batches"],
            },
        )

        response.raise_for_status()

        return response.json()

    @classmethod
    def make_request(cls, repository_files: dict[str, bytes]) -> dict[str, str]:
        request_batches = cls._add_batches_request_metadata(
            cls._get_batched_repository_files(repository_files)
        )

        with ThreadPoolExecutor(max_workers=len(request_batches)) as executor:
            results = executor.map(cls._make_batch_request, request_batches)
            return {"repository_id": result["repository_id"] for result in results}
