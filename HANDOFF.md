# HANDOFF — code_assessment

새 세션에서 이 레포 작업 전에 이 파일부터 읽을 것.

## 목적

빅테크 IT general coding assessment(CodeSignal GCA류) 대비용 연습 툴.
대상 언어는 **Python, Java 두 개만**. 퀴즈/문제 statement는 영문(미국 영어) 기준.
레포는 **public** (WhoisHOO/code_assessment, 2026-09-13에 private→public 전환).

## 현재 상태 (2026-09-13, sprint1)

- **Study UI** (`study.cmd` → `python -m quiz.server` → localhost:8765):
  Daily(Leitner SRS 복습 큐, 신규 하루 10개 캡) / Flashcards(트리거→패턴) /
  Quiz(MCQ) / Problems(타이머 문제풀이 + 오답 4분류 포스트모템) / Stats.
- **Quiz CLI** (`quiz.cmd` → `python -m quiz`): MCQ 세션, `--review`.
- 콘텐츠: MCQ 20개(python/java 각 10), 플래시카드 15개(cards/patterns.json),
  장문 문제 4개(problems/ 아래 카테고리별).
- 테스트 26개 통과, 서버 API 스모크 테스트 완료.

## 문제 재작성 규칙 (중요 — 사용자가 데이터 줄 때)

사용자가 다른 플랫폼(CodeSignal 등)에서 푼 문제를 주면 **원문 그대로 저장 금지**:

1. "무엇을 묻는가"(개념/패턴)만 유지하고 스토리·이름·수치·예시를 전부 바꾼다.
2. 바꾼 예시는 **반드시 솔루션 코드를 실제 실행해서 검증**한 뒤 적는다.
3. Statement(Problem/Examples/Constraints)는 영어 — 실전처럼 영문 스펙 독해
   훈련 목적. Approach 이하 노트는 한국어 허용.
4. `problems/<category>/<id>.md`로 저장 (폴더=카테고리, 로더가 검증).
   형식은 `problems/_TEMPLATE.md`. `## Approach` 헤딩 위=타이머 중 표시,
   아래=Reveal 후 표시라 헤딩 필수.
5. 사용자 본인이 작성한 솔루션 코드는 그대로 유지해도 됨. Python만 있으면
   Java 버전을 추가로 작성.
6. 가능하면 관련 플래시카드(cards/)와 연결하거나 새 카드 추가 검토.

이관 이력: 구 `coding-problems.md`의 3문제를 재작성해 problems/로 이동
(Bob's String Encoding → shifted-frequency-report, Climbing Stairs →
corridor-hops, Merge Intervals → booking-consolidation). 원문은 git 히스토리.
사용자 제공 1호: Group Anagrams → rearranged-aliases.

## 카테고리 (problems/ 폴더)

arrays-intervals, dynamic-programming, graphs-trees, strings-hashing.
필요시 추가 후보: two-pointers-sliding-window, heaps-stacks,
implementation-simulation, math-bits.

## 설계 결정

- **문제 데이터: MCQ/카드 = JSON, 장문 문제 = md(간이 frontmatter).**
  문서(README/HANDOFF)는 md.
- **stdlib only.** pip install 없이 실행. UI도 vanilla JS (CDN 없음, 오프라인 OK).
- `.cmd`는 런처만 (quiz.cmd, study.cmd — python → py 폴백).
- SRS: Leitner 5박스, 간격 1/2/4/8/16일. 오답→박스1+당일 재출제.
  신규 도입 하루 10개 캡. 상태는 `results/study_state.json` (gitignored).
  CLI의 `results/missed.json`은 별도 (CLI 전용).
- 오답 포스트모템 4분류: misread / unknown_pattern / slow_recall /
  implementation_bug (+none). 이게 훈련 방향을 정하는 핵심 데이터.

## 다음 할 일 (sprint2 후보)

- 사용자 제공 문제 계속 재작성·추가 (위 규칙).
- MCQ/카드 확장, GCA 모의 세트 모드(4문제 70분 묶음) 검토.
- Stats에 정답률 추이(시간축) 추가 검토.

## 실행/테스트

```
study.cmd                               # 학습 UI (localhost:8765)
quiz.cmd                                # CLI 퀴즈
python -m unittest discover -s tests    # 테스트
```
