# prompts

LLM 프롬프트는 Python 코드 안에 길게 박지 말고 파일로 분리한다.

권장:
- `simplify_system.txt`
- `training_generate_system.txt`
- `feedback_system.txt`

프롬프트 버전도 응답의 `model_version` 또는 별도 `prompt_version`으로 남긴다.
