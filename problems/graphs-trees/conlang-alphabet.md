---
id: conlang-alphabet
title: Constructed Language Alphabet
category: graphs-trees
difficulty: hard
trigger: "recover a total order from pairwise before/after constraints (sorted words -> letter order)"
pattern: "directed graph from adjacent-word comparison + Kahn topological sort; cycle or prefix violation -> impossible"
time_target_min: 25
---

## Problem

A fantasy game studio invented a constructed language with its own alphabet
order, and shipped a glossary of words sorted lexicographically **by that
alphabet**. The alphabet itself was lost. Implement
`recover_alphabet(words: List[str]) -> str` that returns a string containing
every unique letter appearing in `words`, arranged in an order consistent
with the constraints implied by comparing adjacent words.

If no valid ordering exists — the constraints form a cycle, or a longer word
appears before its own prefix (e.g. `["dax", "da"]`) — return `""`.

If more than one valid ordering satisfies the constraints, any one of them
is accepted.

## Examples

Input: `["sh", "sa", "ha", "hd", "ae", "de"]`
Output: `"sehad"` (one valid answer)

Derived constraints: `sh|sa -> h<a`, `sa|ha -> s<h`, `ha|hd -> a<d`
(later pairs repeat these). `e` appears but is unconstrained, so any
placement of `e` that keeps `s<h`, `h<a`, `a<d` is accepted — `"shade"`
would be valid too.

Input: `["dax", "da"]` → Output: `""` (longer word before its own prefix)
Input: `["d", "s", "d"]` → Output: `""` (`d<s` and `s<d` — a cycle)
Input: `["h"]` → Output: `"h"`

## Constraints

- `1 <= len(words) <= 1000`, `1 <= len(word) <= 100`
- All characters are lowercase English letters (a-z).

## Approach

**문제 이해가 절반이다.** 출력은 "등장하는 문자 나열"이 아니라, **주어진 단어
순서가 성립하도록 하는 알파벳 순서**다. 단어들이 이미 그 언어의 사전순으로
정렬돼 있다는 것이 입력이 주는 정보이고, 우리는 그걸 역으로 추론한다.

핵심 관찰: 사전순 정렬에서 인접한 두 단어를 앞에서부터 비교하면 —

1. **처음으로 다른 문자 쌍이 알파벳 순서 하나를 알려준다.**
   `"sh"` vs `"sa"`: s==s, 그다음 h != a, 그리고 "sh"가 먼저 나왔으므로 `h < a`.
   그 뒤 문자들은 아무 정보도 주지 않는다 (첫 차이가 순서를 결정하니까).
2. **끝까지 같은데 앞 단어가 더 길면 모순.** `["dax", "da"]`: 사전순에서는
   prefix가 항상 먼저 와야 하므로 (영어 사전에서도 ab가 abc보다 앞), 어떤
   알파벳 순서로도 불가능 → `""`. 이 케이스에서는 새 문자 관계가 하나도 안
   나오는데도 invalid라는 점이 함정.

이렇게 얻은 `x < y` 관계들을 방향 그래프 간선 `x → y`로 저장하면, 문제가
**"이 그래프의 위상 정렬(topological sort)을 구하라"**로 바뀐다:

- **Kahn's algorithm (BFS)**: 각 노드의 indegree(들어오는 간선 수)를 세고,
  indegree 0인 노드부터 큐에 넣어 하나씩 꺼내며 이웃의 indegree를 깎는다.
  0이 되는 노드를 큐에 추가.
- **사이클 검사가 공짜로 따라온다**: 큐가 비었는데 결과 길이 < 전체 문자 수면
  사이클 (`d<s`이면서 `s<d` 같은 모순) → `""`.
- 등장만 하고 제약이 없는 문자(예시의 `e`)는 indegree 0이라 자연스럽게
  결과에 포함된다 — 모든 등장 문자를 그래프에 먼저 등록해두는 이유.

단계 요약: ① 모든 문자 등록 → ② 인접 단어 비교로 간선 수집 (+prefix 검사)
→ ③ indegree 계산 → ④ Kahn BFS → ⑤ 길이 검사.

## Complexity

- 시간: **O(C)** — C = 모든 단어의 총 문자 수 (비교가 지배).
  위상 정렬 자체는 O(V + E), V <= 26, E <= words-1이라 사실상 상수.
- 공간: **O(V + E)** = O(1) 수준 (알파벳 26자 상한).

## Solution (Python)

```python
from collections import deque
from typing import List


def recover_alphabet(words: List[str]) -> str:
    # 1. Register every unique character (insertion order = first appearance)
    graph = {char: [] for word in words for char in word}

    # 2. Compare adjacent words to extract ordering constraints
    for i in range(len(words) - 1):
        first, second = words[i], words[i + 1]

        # A longer word may not appear before its own prefix
        if len(first) > len(second) and first.startswith(second):
            return ""

        for j in range(min(len(first), len(second))):
            if first[j] != second[j]:
                a, b = first[j], second[j]
                if b not in graph[a]:
                    graph[a].append(b)
                break  # only the FIRST difference carries information

    # 3. Indegrees
    indegree = {char: 0 for char in graph}
    for char in graph:
        for neighbor in graph[char]:
            indegree[neighbor] += 1

    # 4. Kahn's topological sort (BFS from indegree-0 nodes)
    queue = deque(char for char in indegree if indegree[char] == 0)
    result = []
    while queue:
        char = queue.popleft()
        result.append(char)
        for neighbor in graph[char]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    # 5. Leftover characters mean a cycle -> impossible
    if len(result) != len(graph):
        return ""
    return "".join(result)


if __name__ == "__main__":
    test_cases = [
        ["sh", "sa", "ha", "hd", "ae", "de"],  # "sehad" (one valid order)
        ["dax", "da"],                         # "" (prefix violation)
        ["d", "s", "d"],                       # "" (cycle)
        ["h"],                                 # "h"
    ]
    for words in test_cases:
        print(words, "->", repr(recover_alphabet(words)))
```

구현 디테일 두 가지 (채점에는 26자 상한 덕에 안 걸리지만, 습관으로):

- 큐는 `list.pop(0)`(O(n))이 아니라 `collections.deque.popleft()`(O(1)).
- 중복 간선 검사 `b not in graph[a]`는 리스트 스캔 — 노드가 많은 일반 그래프면
  인접 리스트를 set으로.

## Solution (Java)

```java
import java.util.*;

public class ConlangAlphabet {

    public static String recoverAlphabet(String[] words) {
        // 1. Register every unique character
        Map<Character, List<Character>> graph = new LinkedHashMap<>();
        for (String w : words) {
            for (char c : w.toCharArray()) {
                graph.putIfAbsent(c, new ArrayList<>());
            }
        }

        // 2. Adjacent-word comparison
        for (int i = 0; i < words.length - 1; i++) {
            String first = words[i], second = words[i + 1];
            if (first.length() > second.length() && first.startsWith(second)) {
                return "";
            }
            int limit = Math.min(first.length(), second.length());
            for (int j = 0; j < limit; j++) {
                char a = first.charAt(j), b = second.charAt(j);
                if (a != b) {
                    if (!graph.get(a).contains(b)) {
                        graph.get(a).add(b);
                    }
                    break;
                }
            }
        }

        // 3. Indegrees
        Map<Character, Integer> indegree = new HashMap<>();
        for (char c : graph.keySet()) indegree.put(c, 0);
        for (List<Character> neighbors : graph.values()) {
            for (char b : neighbors) indegree.merge(b, 1, Integer::sum);
        }

        // 4. Kahn's topological sort
        Deque<Character> queue = new ArrayDeque<>();
        for (Map.Entry<Character, Integer> e : indegree.entrySet()) {
            if (e.getValue() == 0) queue.add(e.getKey());
        }
        StringBuilder result = new StringBuilder();
        while (!queue.isEmpty()) {
            char c = queue.poll();
            result.append(c);
            for (char b : graph.get(c)) {
                if (indegree.merge(b, -1, Integer::sum) == 0) queue.add(b);
            }
        }

        // 5. Cycle check
        return result.length() == graph.size() ? result.toString() : "";
    }

    public static void main(String[] args) {
        System.out.println(recoverAlphabet(
            new String[]{"sh", "sa", "ha", "hd", "ae", "de"})); // sehad
        System.out.println("[" + recoverAlphabet(new String[]{"dax", "da"}) + "]"); // []
    }
}
```

## Verification

파이썬 구현을 실행해 확인:

- `["sh","sa","ha","hd","ae","de"]` → `"sehad"` — 예시 단어들이 실제로
  `s<h<a<d<e` 알파벳 기준 정렬 상태임을 별도 코드로 검증했고, 출력이 파생
  제약(s<h, h<a, a<d)을 모두 만족함도 확인.
- `["dax","da"]` → `""`, `["d","s","d"]` → `""`, `["h"]` → `"h"`.

## Post-mortem notes

- 2026-09-13: 막힌 원인은 알고리즘이 아니라 **문제 이해** — 출력을 "등장 문자
  나열"로 오해해서 `["dax","da"]`가 왜 `""`인지부터 막힘 (4분류: misread).
  대응 습관: 코딩 전에 **예제 입출력을 역산해서 문제를 한 문장으로 재진술**할
  것 ("왜 이 입력이 이 출력인가?"를 설명 못 하면 아직 문제를 모르는 것).
  특히 invalid 케이스 예시는 문제의 정의를 가장 정확히 알려주는 힌트다.

관련 플래시카드: card-topological-sort, card-bfs-shortest.
