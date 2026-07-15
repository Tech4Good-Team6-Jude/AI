from app.providers.clients.stt_client import SttClient


class ReadingPipeline:
    def __init__(self, stt_client: SttClient):
        self.stt_client = stt_client

    async def evaluate(
        self,
        *,
        audio: bytes,
        filename: str,
        expected_text: str,
        language: str,
    ) -> dict:
        stt_result = await self.stt_client.transcribe(
            audio=audio,
            filename=filename,
            language=language,
        )

        word_results = self._compare_words(
            expected_text=expected_text,
            spoken_text=stt_result.transcript,
        )

        accuracy = self._calculate_accuracy(word_results)
        completeness = self._calculate_completeness(word_results)

        return {
            "transcript": stt_result.transcript,
            "accuracy": accuracy,
            "completeness": completeness,
            "word_results": word_results,
        }

    def _compare_words(
        self,
        *,
        expected_text: str,
        spoken_text: str,
    ) -> list[dict]:
        expected_words = expected_text.split()
        spoken_words = spoken_text.split()

        results = []

        for index, expected in enumerate(expected_words):
            spoken = spoken_words[index] if index < len(spoken_words) else ""

            results.append(
                {
                    "expected": expected,
                    "spoken": spoken,
                    "status": "CORRECT" if expected == spoken else "MISPRONOUNCED",
                }
            )

        return results

    def _calculate_accuracy(self, results: list[dict]) -> int:
        if not results:
            return 0

        correct = sum(item["status"] == "CORRECT" for item in results)
        return round(correct / len(results) * 100)

    def _calculate_completeness(self, results: list[dict]) -> int:
        if not results:
            return 0

        spoken = sum(bool(item["spoken"]) for item in results)
        return round(spoken / len(results) * 100)