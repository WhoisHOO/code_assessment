---
id: terrain-rainwater
title: Rainwater on a Terrain Grid
category: heaps-stacks
difficulty: hard
trigger: "trapped water volume on a 2D height grid (water can leak in any of 4 directions)"
pattern: "min-heap flood fill from the boundary - always expand from the lowest wall (Dijkstra-style)"
time_target_min: 25
---

## Problem

A drainage survey models a plot of land as an `m x n` grid of integer
elevations. After a rainstorm, water collects wherever the terrain forms a
basin, and drains off the edges of the grid. Implement
`trapped_water(terrain)` that returns the total volume of water trapped.

(This is the 2D-grid generalization of the classic 1D trapping-rain-water
problem: here water can escape in any of the 4 directions, not just left or
right.)

## Examples

Input:
```
[[4, 4, 4, 4],
 [4, 1, 2, 4],
 [4, 4, 4, 4]]
```
Output: `5` — the two inner cells fill up to the surrounding wall height 4:
(4-1) + (4-2) = 5.

Input:
```
[[4, 4, 4, 4],
 [1, 1, 2, 4],
 [4, 4, 4, 4]]
```
Output: `0` — the same basin leaks out through the height-1 cell on the left
edge, so nothing is trapped.

## Constraints

- `1 <= m, n <= 200`, `0 <= terrain[r][c] <= 2 * 10^4`.
- A grid smaller than 3x3 cannot trap any water.

## Approach

**1D 직관이 왜 그대로 안 통하나**: 1D에서는 물 높이가 "왼쪽 최대 벽과 오른쪽
최대 벽의 min"이라 two-pointer로 끝난다. 2D에서는 물이 **4방향 어디로든 샐 수
있어서**, 셀의 수위 = "바깥까지 나가는 모든 경로 중, 경로상 최대 벽이 가장
낮은 경로의 그 벽 높이"가 된다. 경로 개념이 들어오는 순간 이건 그래프 문제다.

**핵심 발상 — 경계에서 가장 낮은 벽부터 안으로 조인다**:

1. 경계 셀은 물을 가둘 수 없다 (바로 바깥으로 흐름). 경계 전체를 min-heap에
   넣는다.
2. heap에서 **가장 낮은 셀**을 꺼낸다. 이 셀의 높이가 현재 "수위 후보"다.
   Dijkstra와 같은 논리로, 지금 꺼낸 높이보다 낮은 탈출구는 존재할 수 없다
   (있었다면 먼저 꺼내졌을 것) — 그래서 이 수위는 확정이다.
3. 방문 안 한 이웃을 본다: 이웃이 수위보다 낮으면 `수위 - 이웃높이`만큼 물이
   고인다. 이웃을 heap에 넣을 때는 `max(수위, 이웃높이)`로 넣는다 — 물이 찬
   셀은 그 수위가 새로운 벽 역할을 하기 때문.
4. heap이 빌 때까지 반복. 모든 셀이 정확히 한 번씩 처리된다.

한 줄 요약: **"밖에서부터 물을 부어가며, 항상 가장 낮은 둑을 먼저 넘긴다"**.
이 "가장 낮은 것부터 확정" 구조가 Dijkstra/Prim과 같은 계열이라 min-heap이
자연스럽다.

## Complexity

- 시간: **O(mn log(mn))** — 셀마다 heap push/pop 한 번.
- 공간: **O(mn)** — visited + heap.

## Solution (Python)

```python
import heapq


def trapped_water(terrain):
    if not terrain or not terrain[0]:
        return 0
    m, n = len(terrain), len(terrain[0])
    if m < 3 or n < 3:
        return 0  # no interior cell can hold water

    visited = [[False] * n for _ in range(m)]
    heap = []

    # Seed the heap with every boundary cell
    for r in range(m):
        heapq.heappush(heap, (terrain[r][0], r, 0))
        visited[r][0] = True
        heapq.heappush(heap, (terrain[r][n - 1], r, n - 1))
        visited[r][n - 1] = True
    for c in range(1, n - 1):
        heapq.heappush(heap, (terrain[0][c], 0, c))
        visited[0][c] = True
        heapq.heappush(heap, (terrain[m - 1][c], m - 1, c))
        visited[m - 1][c] = True

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    water = 0

    # Always process the lowest wall first
    while heap:
        height, r, c = heapq.heappop(heap)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= m or nc < 0 or nc >= n or visited[nr][nc]:
                continue
            visited[nr][nc] = True

            neighbor_height = terrain[nr][nc]
            if neighbor_height < height:
                water += height - neighbor_height  # fills up to the wall

            # A filled cell acts as a wall at the water level
            heapq.heappush(heap, (max(height, neighbor_height), nr, nc))

    return water


if __name__ == "__main__":
    print(trapped_water([[4, 4, 4, 4],
                         [4, 1, 2, 4],
                         [4, 4, 4, 4]]))  # 5
    print(trapped_water([[4, 4, 4, 4],
                         [1, 1, 2, 4],
                         [4, 4, 4, 4]]))  # 0 (leaks out the left edge)
```

## Solution (Java)

```java
import java.util.*;

public class TerrainRainwater {

    public static int trappedWater(int[][] terrain) {
        if (terrain.length < 3 || terrain[0].length < 3) {
            return 0;
        }
        int m = terrain.length, n = terrain[0].length;
        boolean[][] visited = new boolean[m][n];
        PriorityQueue<int[]> heap =
            new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));

        // Seed the heap with every boundary cell
        for (int r = 0; r < m; r++) {
            for (int c = 0; c < n; c++) {
                if (r == 0 || r == m - 1 || c == 0 || c == n - 1) {
                    heap.add(new int[]{terrain[r][c], r, c});
                    visited[r][c] = true;
                }
            }
        }

        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int water = 0;

        while (!heap.isEmpty()) {
            int[] cell = heap.poll();
            int height = cell[0], r = cell[1], c = cell[2];
            for (int[] d : dirs) {
                int nr = r + d[0], nc = c + d[1];
                if (nr < 0 || nr >= m || nc < 0 || nc >= n || visited[nr][nc]) {
                    continue;
                }
                visited[nr][nc] = true;
                int nh = terrain[nr][nc];
                if (nh < height) {
                    water += height - nh;
                }
                heap.add(new int[]{Math.max(height, nh), nr, nc});
            }
        }
        return water;
    }

    public static void main(String[] args) {
        System.out.println(trappedWater(new int[][]{
            {4, 4, 4, 4}, {4, 1, 2, 4}, {4, 4, 4, 4}}));  // 5
    }
}
```

## Verification

파이썬 구현을 실행해 확인: 닫힌 분지 → `5`, 왼쪽 가장자리로 새는 같은 분지 →
`0`, 포켓 지형 `[[2,3,2],[3,1,3],[2,3,2],[3,3,3]]` → `2` (가운데 1이 수위
3까지 참), 3행 미만 그리드 → `0`.

관련 플래시카드: card-heap-flood-fill, card-heap-topk, card-bfs-shortest.
