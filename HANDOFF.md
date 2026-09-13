# HANDOFF — code_assessment

새 세션에서 이 레포 작업 전에 이 파일부터 읽을 것.

## 목적

빅테크 IT general coding assessment 대비용 랜덤 퀴즈 CLI.
대상 언어는 **Python, Java 두 개만**. 퀴즈 콘텐츠는 영문(미국 영어) 기준.
레포는 private (WhoisHOO/code_assessment).

## 현재 상태 (2026-09-13, sprint1)

- sprint1 브랜치에 뼈대 완성: stdlib-only 파이썬 패키지 `quiz/` + JSON 문제은행.
- 문제 20개 시드 (python 10 + java 10, `questions/*/core.json`).
- unittest 스위트 통과 확인, 실제 실행 검증 완료.
- `coding-problems.md`는 퀴즈 툴과 별개의 장문 문제풀이 정리 (main에서 온 기존 파일).

## 설계 결정

- **문제 데이터 = JSON, 문서/메모 = md.** 랜덤 추출·보기 셔플·필터·검증이
  필요해서 문제은행은 구조화된 JSON. md는 사람이 읽는 문서(README, HANDOFF,
  coding-problems)에만 사용.
- **stdlib only.** pip install 없이 `python -m quiz`로 즉시 실행되는 게 목표.
- **quiz.cmd는 Windows용 얇은 런처일 뿐** (python → py 폴백 포함). 본체는
  파이썬이라 macOS/Linux에서도 `python -m quiz`로 동일하게 동작.
- 보기 순서는 런타임에 셔플 → JSON의 `answer_index`는 원본 순서 기준.
- 오답은 `results/missed.json`(gitignore됨)에 누적, `--review`로 재출제.
  맞히면 목록에서 제거됨.

## 다음 할 일 (sprint2 후보)

- 문제은행 확장 (topic별 파일 분리: algorithms.json, concurrency.json 등).
- 출력 예측형 외 유형 추가 검토 (빈칸 채우기, 코드 순서 맞추기).
- 세션 통계 누적 (topic별 정답률 추이) — results/ 아래 세션 로그.
- coding-problems.md의 문제를 퀴즈 문항으로 변환하는 규칙 정하기.

## 실행/테스트

```
quiz.cmd                                # 또는 python -m quiz
python -m unittest discover -s tests    # 테스트
```
