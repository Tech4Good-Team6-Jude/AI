class LlmClient:
    async def simplify(
        self,
        *,
        text: str,
        target_reading_level: int,
        include_definitions: bool,
    ) -> dict:
        # LLM 호출
        # 프롬프트는 app/prompts에 파일로 보관
        raise NotImplementedError