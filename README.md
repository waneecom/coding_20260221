# SJW AI

PySide6 기반의 데스크톱 GUI 도구입니다.  
한 화면에서 아래 3가지 기능을 제공합니다.

- 위키백과 검색 (한국어 위키 요약 조회)
- 다음 맞춤법 검사
- Google 번역

## 실행 환경

- Python 3.12 이상
- Windows (현재 프로젝트 기준)

## 설치

프로젝트 루트에서:

```bash
uv sync
```

또는 기존 가상환경(`.venv`)을 사용하는 경우 필요한 패키지를 설치합니다.

## 개발 모드 실행

```bash
.venv\Scripts\python.exe main.py
```

## 실행파일(단독 EXE)

현재 배포용 단일 실행파일:

- `dist/SJW AI.exe`

이 파일은 단독 실행(onefile) 기준으로 빌드되어, 다른 폴더로 복사해도 실행할 수 있도록 구성되어 있습니다.

## EXE 빌드

```bash
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name "SJW AI" --icon "sjwai.ico" --add-binary "C:\Users\burpa\AppData\Local\Python\pythoncore-3.12-64\DLLs\_socket.pyd;." --add-binary "C:\Users\burpa\AppData\Local\Python\pythoncore-3.12-64\DLLs\select.pyd;." main.py
```

## 주요 파일

- `main.py`: 메인 GUI 및 기능 로직
- `pyproject.toml`: 프로젝트 의존성/메타데이터
- `sjwai.ico`: 실행파일 아이콘
- `dist/SJW AI.exe`: 빌드 결과물

## 의존성

- `PySide6`
- `requests`
- `deep-translator`
- `PyInstaller` (빌드용)

## 동작 개요

1. 메인 창에서 기능 선택
2. 각 기능 창에서 입력 후 실행
3. 네트워크 요청 결과를 화면에 표시

## 주의사항

- 검색/맞춤법/번역 기능은 외부 서비스 호출이 필요하므로 인터넷 연결이 필요합니다.
- 외부 API 응답 형식 변경 시 일부 결과 형식이 달라질 수 있습니다.
