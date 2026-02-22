# -*- coding: utf-8 -*-
# 인터프리터: c:\Users\burpa\vibe_coding\SJW\바이브 코딩20260205\.venv\Scripts\python.exe

import sys
import os

# UTF-8 모드가 아니면 자동 재시작 (한국어 인코딩 오류 방지)
if __name__ == "__main__" and not getattr(sys, "frozen", False) and sys.flags.utf8_mode == 0:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    os.execvpe(sys.executable, [sys.executable, "-X", "utf8"] + sys.argv, env)

import re
import webbrowser
import urllib.parse
import requests
from deep_translator import GoogleTranslator

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QMessageBox, QComboBox, QLineEdit, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont


# ──────────────────────────────────────────────
# 공통 스타일
# ──────────────────────────────────────────────
FONT_KO = QFont("맑은 고딕", 11)

# 결과창 — 검정 배경 흰 글씨
RESULT_BOX = (
    "QTextEdit {"
    "  background:#1e1e1e;"
    "  color:#e8e8e8;"
    "  border:1px solid #444;"
    "  border-radius:4px;"
    "}"
)


# ──────────────────────────────────────────────
# 다음(카카오) 맞춤법 검사
# ──────────────────────────────────────────────
def daum_spell_check(text: str) -> str:
    url = "https://dic.daum.net/grammar_checker.do"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://dic.daum.net/grammar_checker.do",
    }
    resp = requests.post(url, data={"sentence": text}, headers=headers, timeout=15)
    resp.encoding = "utf-8"

    pattern = re.compile(
        r'data-error-input="([^"]+)"\s+data-error-output="([^"]+)"'
    )
    errors = pattern.findall(resp.text)

    corrected = text
    for wrong, fixed in errors:
        corrected = corrected.replace(wrong, fixed, 1)

    if not errors:
        return "✅ 맞춤법이 올바릅니다! 틀린 곳이 없습니다."

    lines = [f"⚠️  총 {len(errors)}개의 오류가 발견됐습니다.\n"]
    lines.append(f"📝 [교정된 문장]\n{corrected}\n")
    lines.append("🔍 [오류 목록]")
    for wrong, fixed in errors:
        lines.append(f"  ✗  '{wrong}'  →  ✓  '{fixed}'")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 구글 번역
# ──────────────────────────────────────────────
LANG_MAP = {
    "영어": "en",
    "일본어": "ja",
    "중국어(간체)": "zh-CN",
    "중국어(번체)": "zh-TW",
    "스페인어": "es",
    "프랑스어": "fr",
    "독일어": "de",
    "한국어": "ko",
}

def google_translate(text: str, target_lang: str) -> str:
    lang_code = LANG_MAP.get(target_lang, "en")
    return GoogleTranslator(source="auto", target=lang_code).translate(text)


# ──────────────────────────────────────────────
# 위키백과 검색
# ──────────────────────────────────────────────
def search_wikipedia(term: str) -> str:
    encoded = urllib.parse.quote(term)
    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    headers = {"User-Agent": "SJW-AI-App/1.0 (educational project)"}
    resp = requests.get(url, headers=headers, timeout=10)

    if resp.status_code == 404:
        # 검색 API로 대체
        search_url = "https://ko.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": term,
            "format": "json",
            "utf8": 1,
            "srlimit": 1,
        }
        s = requests.get(search_url, params=params, headers=headers, timeout=10)
        results = s.json().get("query", {}).get("search", [])
        if not results:
            return f"❌ '{term}'에 대한 위키백과 문서를 찾을 수 없습니다."
        # 첫 번째 결과로 재시도
        title = results[0]["title"]
        encoded2 = urllib.parse.quote(title)
        resp = requests.get(
            f"https://ko.wikipedia.org/api/rest_v1/page/summary/{encoded2}",
            headers=headers, timeout=10
        )

    data = resp.json()
    title = data.get("title", term)
    desc = data.get("description", "")
    extract = data.get("extract", "내용을 찾을 수 없습니다.")

    lines = []
    lines.append(f"📖  {title}")
    if desc:
        lines.append(f"    {desc}\n")
    lines.append(extract)
    lines.append(f"\n🔗  출처: 한국어 위키백과")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 작업 스레드
# ──────────────────────────────────────────────
class WorkerThread(QThread):
    result_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            self.result_ready.emit(self.func(*self.args))
        except Exception as e:
            self.error_occurred.emit(f"❌ 오류 발생:\n{e}")


# ──────────────────────────────────────────────
# 기본 다이얼로그
# ──────────────────────────────────────────────
class BaseDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 320)
        self.resize(640, 540)
        self.thread = None

    def _back_btn(self):
        btn = QPushButton("◀  이전")
        btn.setFixedHeight(36)
        btn.setStyleSheet(
            "QPushButton{background:#555;color:white;border-radius:6px;font-size:13px;padding:6px;}"
            "QPushButton:hover{background:#444;}"
        )
        btn.clicked.connect(self.close)
        return btn

    def _clear_btn(self, slot):
        btn = QPushButton("초기화")
        btn.setFixedHeight(36)
        btn.setStyleSheet(
            "QPushButton{background:#e53935;color:white;border-radius:6px;font-size:13px;padding:6px;}"
            "QPushButton:hover{background:#c62828;}"
        )
        btn.clicked.connect(slot)
        return btn

    def _on_result(self, result: str):
        self.result_text.setPlainText(result)
        self.status_label.setText("완료!")
        self.run_btn.setEnabled(True)

    def _on_error(self, error: str):
        self.result_text.setPlainText(error)
        self.status_label.setText("오류 발생")
        self.run_btn.setEnabled(True)

    def _start(self, func, *args):
        self.run_btn.setEnabled(False)
        self.result_text.setPlainText("")
        self.status_label.setText("처리 중... 잠시만 기다려주세요.")
        self.thread = WorkerThread(func, *args)
        self.thread.result_ready.connect(self._on_result)
        self.thread.error_occurred.connect(self._on_error)
        self.thread.start()


# ──────────────────────────────────────────────
# 검색 다이얼로그
# ──────────────────────────────────────────────
class SearchDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("검색 도움이 AI  |  위키백과", parent)
        self._namu_term = ""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # 검색창 행
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색할 단어를 입력하세요...")
        self.search_input.setFixedHeight(38)
        self.search_input.setFont(FONT_KO)
        self.search_input.setStyleSheet("font-size:13px; padding:4px 8px;")
        self.search_input.returnPressed.connect(self._run)

        self.run_btn = QPushButton("검색")
        self.run_btn.setFixedHeight(38)
        self.run_btn.setFixedWidth(80)
        self.run_btn.setStyleSheet(
            "QPushButton{background:#1976D2;color:white;border-radius:6px;font-size:13px;}"
            "QPushButton:hover{background:#1565C0;}"
            "QPushButton:disabled{background:#aaa;}"
        )
        self.run_btn.clicked.connect(self._run)

        search_row.addWidget(self.search_input)
        search_row.addWidget(self.run_btn)
        layout.addLayout(search_row)

        # 결과창
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(FONT_KO)
        self.result_text.setStyleSheet(RESULT_BOX)
        layout.addWidget(self.result_text)

        # 하단 버튼 행
        btn_row = QHBoxLayout()

        self.namu_btn = QPushButton("나무위키에서 열기")
        self.namu_btn.setFixedHeight(36)
        self.namu_btn.setEnabled(False)
        self.namu_btn.setStyleSheet(
            "QPushButton{background:#ff6f00;color:white;border-radius:6px;font-size:13px;padding:6px;}"
            "QPushButton:hover{background:#e65100;}"
            "QPushButton:disabled{background:#555;color:#888;}"
        )
        self.namu_btn.clicked.connect(self._open_namu)

        btn_row.addWidget(self.namu_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._clear_btn(self._clear))
        btn_row.addWidget(self._back_btn())
        layout.addLayout(btn_row)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color:gray;font-size:11px;")
        layout.addWidget(self.status_label)

    def _run(self):
        term = self.search_input.text().strip()
        if not term:
            QMessageBox.warning(self, "입력 필요", "검색할 단어를 입력해주세요.")
            return
        self._namu_term = term
        self.namu_btn.setEnabled(False)
        self._start(search_wikipedia, term)

    def _on_result(self, result: str):
        self.result_text.setPlainText(result)
        self.status_label.setText("완료!")
        self.run_btn.setEnabled(True)
        self.namu_btn.setEnabled(True)

    def _open_namu(self):
        term = urllib.parse.quote(self._namu_term)
        webbrowser.open(f"https://namu.wiki/w/{term}")

    def _clear(self):
        self.search_input.clear()
        self.result_text.clear()
        self.status_label.setText("")
        self._namu_term = ""
        self.namu_btn.setEnabled(False)


# ──────────────────────────────────────────────
# 맞춤법 검사 다이얼로그
# ──────────────────────────────────────────────
class SpellCheckDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("맞춤법 도움이 AI  |  다음 맞춤법 검사기", parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(QLabel("검사할 텍스트 입력:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("여기에 맞춤법을 검사할 텍스트를 입력하세요...")
        self.input_text.setFont(FONT_KO)
        self.input_text.setMaximumHeight(150)
        layout.addWidget(self.input_text)

        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("맞춤법 검사")
        self.run_btn.setFixedHeight(36)
        self.run_btn.setStyleSheet(
            "QPushButton{background:#4CAF50;color:white;border-radius:6px;font-size:13px;padding:6px;}"
            "QPushButton:hover{background:#45a049;}"
            "QPushButton:disabled{background:#aaa;}"
        )
        self.run_btn.clicked.connect(self._run)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self._clear_btn(self._clear))
        btn_row.addWidget(self._back_btn())
        layout.addLayout(btn_row)

        layout.addWidget(QLabel("검사 결과:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(FONT_KO)
        self.result_text.setStyleSheet(RESULT_BOX)
        layout.addWidget(self.result_text)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color:gray;font-size:11px;")
        layout.addWidget(self.status_label)

    def _run(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "입력 필요", "검사할 텍스트를 입력해주세요.")
            return
        self._start(daum_spell_check, text)

    def _clear(self):
        self.input_text.clear()
        self.result_text.clear()
        self.status_label.setText("")


# ──────────────────────────────────────────────
# 번역 다이얼로그
# ──────────────────────────────────────────────
class TranslateDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("번역 도움이 AI  |  Google 번역", parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("번역 대상 언어:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(list(LANG_MAP.keys()))
        self.lang_combo.setFixedHeight(32)
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        layout.addWidget(QLabel("번역할 텍스트 입력:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("여기에 번역할 텍스트를 입력하세요...")
        self.input_text.setFont(FONT_KO)
        self.input_text.setMaximumHeight(150)
        layout.addWidget(self.input_text)

        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("번역하기")
        self.run_btn.setFixedHeight(36)
        self.run_btn.setStyleSheet(
            "QPushButton{background:#1976D2;color:white;border-radius:6px;font-size:13px;padding:6px;}"
            "QPushButton:hover{background:#1565C0;}"
            "QPushButton:disabled{background:#aaa;}"
        )
        self.run_btn.clicked.connect(self._run)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self._clear_btn(self._clear))
        btn_row.addWidget(self._back_btn())
        layout.addLayout(btn_row)

        layout.addWidget(QLabel("번역 결과:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(FONT_KO)
        self.result_text.setStyleSheet(RESULT_BOX)
        layout.addWidget(self.result_text)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color:gray;font-size:11px;")
        layout.addWidget(self.status_label)

    def _run(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "입력 필요", "번역할 텍스트를 입력해주세요.")
            return
        self._start(google_translate, text, self.lang_combo.currentText())

    def _clear(self):
        self.input_text.clear()
        self.result_text.clear()
        self.status_label.setText("")


# ──────────────────────────────────────────────
# 메인 창
# ──────────────────────────────────────────────
class MainWindow:
    def __init__(self):
        self.window = QWidget()
        self.window.setWindowTitle("SJW AI")
        self.window.resize(380, 240)

        layout = QVBoxLayout(self.window)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("SJW AI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:24px; font-weight:700; color:#1f2937;")
        layout.addWidget(title)

        subtitle = QLabel("원하는 기능을 선택하세요")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size:13px; color:#6b7280;")
        layout.addWidget(subtitle)

        layout.addSpacing(6)

        search_btn = QPushButton("위키백과 검색")
        spell_btn = QPushButton("맞춤법 검사")
        trans_btn = QPushButton("번역")
        for btn in (search_btn, spell_btn, trans_btn):
            btn.setFixedHeight(42)
            btn.setStyleSheet(
                "QPushButton{background:#1976D2;color:white;border:none;border-radius:8px;font-size:14px;font-weight:600;}"
                "QPushButton:hover{background:#1565C0;}"
            )
            layout.addWidget(btn)

        search_btn.clicked.connect(lambda: SearchDialog(self.window).exec())
        spell_btn.clicked.connect(lambda: SpellCheckDialog(self.window).exec())
        trans_btn.clicked.connect(lambda: TranslateDialog(self.window).exec())

        layout.addStretch()
        self.window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    try:
        main_win = MainWindow()
    except Exception as e:
        QMessageBox.critical(None, "실행 오류", str(e))
        sys.exit(1)
    sys.exit(app.exec())
