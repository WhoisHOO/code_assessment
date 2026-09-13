---
id: task-dependency-check
title: Task Dependency Feasibility
category: graphs-trees
difficulty: medium
trigger: "'X must run before Y' pairs - can everything finish? (cycle detection in dependencies)"
pattern: "directed graph + Kahn's indegree BFS; all nodes processed = no cycle"
time_target_min: 15
---

## Problem

A job scheduler runs `num_tasks` tasks labeled `0` to `num_tasks - 1`.
You're given a list of dependency pairs where `dependencies[i] = [a, b]`
means task `b` must finish before task `a` can start.

Write `can_complete(num_tasks: int, dependencies: list[list[int]]) -> bool`
that returns whether every task can eventually run — i.e., whether the
dependency graph is free of cycles. Required: **O(V + E)** time.

## Examples

Input: `num_tasks = 5`, `dependencies = [[2,0],[2,1],[3,2],[4,3]]`
Output: `True` (one valid order: 0, 1 → 2 → 3 → 4)

Input: `num_tasks = 3`, `dependencies = [[0,1],[1,2],[2,0]]`
Output: `False` (0 needs 1, 1 needs 2, 2 needs 0 — a cycle)

## Constraints

- `1 <= num_tasks <= 10^5`, `0 <= len(dependencies) <= 5000`
- `dependencies[i].length == 2`, all pairs unique.

## Approach

**이 문제의 절반은 "이게 그래프 문제"라는 걸 알아채는 것이다.** 신호 단어:
"prerequisite / depends on / must run before / can finish all?" → 의존 관계
방향 그래프 + "전부 끝낼 수 있나?" = **사이클 검사** = 위상 정렬이 끝까지
도는지 확인. [[conlang-alphabet]]과 같은 계열 — 거기선 위상 정렬의 *결과
순서*가 답이고, 여기선 *완주 여부*만 답이다.

**간선 방향이 최대 함정**: `[a, b]` = "b를 먼저" → 간선은 `b → a`.

```
for a, b in dependencies:
    graph[b].append(a)   # b가 끝나면 a가 풀린다
    indegree[a] += 1     # a는 선행 조건이 하나 늘었다
```

방향을 반대로 적어도 사이클 유무 자체는 같아서 이 문제는 우연히 통과하지만,
순서까지 출력하는 변형(외계 사전, 빌드 순서)에서는 바로 오답이 된다.
습관적으로 "선행 → 후행"으로 고정할 것.

**Kahn's indegree BFS**:

1. indegree 0인(선행 조건 없는) 태스크를 전부 큐에 넣는다.
2. 하나 꺼내 "완료" 처리하고, 그 태스크를 기다리던 태스크들의 indegree를
   1씩 깎는다. 0이 되면 큐에 추가.
3. 끝났을 때 `완료 수 == num_tasks`면 사이클 없음. 사이클 안의 노드들은
   indegree가 절대 0이 되지 않아 처리되지 못한 채 남는다 — 두 번째 예시는
   시작부터 indegree 0인 노드가 없어서 completed=0으로 끝난다.

DFS 3색(white/gray/black) 검사로도 풀 수 있지만, 면접에서는 Kahn 쪽이 사이클
검사와 순서 출력을 같은 코드로 처리해서 확장 질문("순서도 출력해봐" = Course
Schedule II)에 유리하다.

## Complexity

- 시간: **O(V + E)** — 각 태스크와 간선을 한 번씩 처리.
- 공간: **O(V + E)** — 인접 리스트 + indegree + 큐.

## Solution (Python)

```python
from collections import deque


def can_complete(num_tasks: int, dependencies: list[list[int]]) -> bool:
    # graph[b] = tasks unblocked when b finishes
    graph = [[] for _ in range(num_tasks)]
    indegree = [0] * num_tasks

    for a, b in dependencies:
        graph[b].append(a)
        indegree[a] += 1

    # Start from tasks with no prerequisites
    queue = deque(t for t in range(num_tasks) if indegree[t] == 0)
    completed = 0

    while queue:
        task = queue.popleft()
        completed += 1
        for next_task in graph[task]:
            indegree[next_task] -= 1
            if indegree[next_task] == 0:
                queue.append(next_task)

    # Every task processed <=> no cycle
    return completed == num_tasks


if __name__ == "__main__":
    print(can_complete(5, [[2, 0], [2, 1], [3, 2], [4, 3]]))  # True
    print(can_complete(3, [[0, 1], [1, 2], [2, 0]]))          # False
```

## Solution (Java)

```java
import java.util.*;

public class TaskDependencyCheck {

    public static boolean canComplete(int numTasks, int[][] dependencies) {
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < numTasks; i++) {
            graph.add(new ArrayList<>());
        }
        int[] indegree = new int[numTasks];

        for (int[] dep : dependencies) {
            int a = dep[0], b = dep[1];   // b before a  =>  edge b -> a
            graph.get(b).add(a);
            indegree[a]++;
        }

        Deque<Integer> queue = new ArrayDeque<>();
        for (int t = 0; t < numTasks; t++) {
            if (indegree[t] == 0) queue.add(t);
        }

        int completed = 0;
        while (!queue.isEmpty()) {
            int task = queue.poll();
            completed++;
            for (int next : graph.get(task)) {
                if (--indegree[next] == 0) queue.add(next);
            }
        }
        return completed == numTasks;
    }

    public static void main(String[] args) {
        System.out.println(canComplete(5,
            new int[][]{{2, 0}, {2, 1}, {3, 2}, {4, 3}}));  // true
        System.out.println(canComplete(3,
            new int[][]{{0, 1}, {1, 2}, {2, 0}}));          // false
    }
}
```

## Verification

파이썬 구현을 실행해 확인: 선형+분기 의존 5태스크 → `True`, 3-사이클 →
`False`, 의존성 없음 → `True`, 2-사이클 → `False`.

## Post-mortem notes

- 2026-09-13: 막힌 지점은 구현이 아니라 **문제 → 패턴 분류** (4분류:
  unknown_pattern). "prerequisite/before/can finish all" 같은 신호 단어에서
  그래프+위상 정렬로 연결하는 회로가 아직 자동이 아님 — 정확히 플래시카드
  (card-topological-sort)가 훈련하는 지점. 코테 실력의 절반 이상이 이 분류
  단계라는 점을 재확인한 문제.

관련 플래시카드: card-topological-sort. 관련 문제: conlang-alphabet
(같은 패턴, 순서 복원 버전).
