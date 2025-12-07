# mcp_tool_vision

텍스트 입력만 지원하는 모델에게 이미지를 전달하기 위한 MCP 도구입니다. 이미지 파일을 base64로 변환하고, 선택한 시스템 프롬프트와
 함께 모델에 전달할 사용자 메시지를 만들어 줍니다.

## 특징
- FastMCP 기반(httpx 포함) 구현으로 `/chat/completions` 호출 안정성 향상
- "General", "OCR", "Click", "Find" 네 가지 시스템 프롬프트 프리셋 제공
- 이미지 파일 경로와 명령어(프롬프트)를 받아 JSON 또는 읽기 쉬운 텍스트로 출력
- `/chat/completions`와 동일한 API 명세를 가진 서버로 즉시 요청 가능

## 설치 및 실행
이 프로젝트는 [uv](https://github.com/astral-sh/uv)를 가정합니다. 로컬에서 바로 실행하려면 `uvx`로 스크립트를 호출할 수 있습니다
.

```bash
# 도움말 확인
uvx --from . mcp-tool-vision --help

# 예시 실행 (이미지 경로, 명령어, 시스템 프롬프트 선택)
uvx --from . mcp-tool-vision sample.png "청구서를 OCR로 읽어줘" --prompt OCR --json

# 서버에 바로 호출 (/chat/completions 명세, 환경변수 기본값 사용)
export MCP_VISION_API_URL="https://your-server.example.com"
export MCP_VISION_MODEL="gpt-4o-mini"
uvx --from . mcp-tool-vision sample.png "내용을 요약해줘" --call --json
```

위 명령은 시스템 프롬프트와 사용자 메시지를 모두 포함한 JSON을 표준 출력으로 작성합니다. JSON 없이 사람이 읽기 좋은 형태로 보고
싶다면 `--json` 옵션을 빼면 됩니다. `--call` 옵션을 사용하면 시스템/사용자 메시지로 즉시 `/chat/completions` 요청을 보냅니다.

## 출력 형식
`--json` 옵션을 사용하면 다음 키를 포함하는 객체가 반환됩니다.
- `system`: 선택된 시스템 프롬프트 텍스트
- `user`: `command`, `image_base64`, `filename`, `mime_type`을 포함하는 사용자 메시지(JSON 문자열)
- `summary`: 전달 방법에 대한 요약 문구

`--call`과 함께 `--json`을 쓰면 `request`(엔드포인트·모델·메시지)와 `response`(서버 응답) 구조로 출력됩니다. 텍스트 출력 모드에서는 위 내용과 함께 모델 응답을 그대로 표시합니다.

## 환경변수
- `MCP_VISION_API_URL`: 호출할 서버의 기본 URL (필수)
- `MCP_VISION_MODEL`: `/chat/completions`에 전달할 모델명 (필수)
- `MCP_VISION_API_KEY`: Authorization 헤더에 넣을 토큰 (선택)

CLI 옵션으로 동일한 값을 덮어쓸 수 있습니다.

## 시스템 프롬프트 프리셋
- **General**: 이미지와 지시사항을 요약하고 응답
- **OCR**: 이미지에 포함된 모든 텍스트를 추출
- **Click**: 클릭 대상의 좌표를 (x, y) 픽셀 기준으로 반환
- **Find**: 찾고자 하는 항목의 위치를 짧게 설명

## 개발 메모
- FastMCP 의존성(및 포함된 httpx/pydantic 스택)을 사용합니다.
