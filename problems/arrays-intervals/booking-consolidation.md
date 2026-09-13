---
id: booking-consolidation
title: Booking Consolidation
category: arrays-intervals
difficulty: medium
trigger: "unsorted ranges that overlap must be merged/consolidated"
pattern: "sort by start + single sweep against the last kept interval"
time_target_min: 15
---

## Problem

A meeting-room system stores bookings as an **unsorted** list of intervals
`[start, end]`. Overlapping or touching bookings should be shown as one
consolidated block. Merge all overlapping intervals and return the resulting
non-overlapping intervals **sorted by start time in ascending order**.

Two bookings that merely touch (one ends exactly when the next starts, e.g.
`[1,4]` and `[4,5]`) also count as one block.

## Examples

Input: `[[5,8],[1,3],[2,4],[10,12]]`
Output: `[[1,4],[5,8],[10,12]]`
(`[1,3]` and `[2,4]` overlap and merge into `[1,4]`; the rest are disjoint.)

Input: `[[1,4],[4,5]]`
Output: `[[1,5]]` (touching intervals merge)

## Constraints

- Each interval satisfies `start <= end`. An empty list returns an empty list.
- Target complexity: sort once, then a single pass — **O(n log n)**.

## Approach

1. **시작 시각 기준으로 정렬**한다. 정렬해두면 "지금 보는 구간이 직전에 합쳐둔
   구간과 겹치는지"만 확인하면 되므로, 뒤쪽 구간이 앞쪽 구간과 겹치는지 되짚어볼
   필요가 없어진다 (정렬이 문제를 1차원 순회로 바꿔준다).
2. 결과 리스트를 유지하면서 정렬된 구간을 하나씩 본다:
   - 결과 리스트 **마지막 구간의 end** >= 현재 구간의 **start**이면 겹치거나
     맞닿음 → 마지막 구간의 end를 `max(마지막.end, 현재.end)`로 갱신
     (현재 구간이 완전히 포함되는 경우, 예: `[1,4]`와 `[2,3]`도 max로 자연 처리).
   - 겹치지 않으면 현재 구간을 새로 추가.
3. 정렬된 순서로 처리했으므로 결과는 이미 시작 시각 오름차순.

값 범위 제약이 없으면 비교 기반 정렬 하한이 O(n log n)이라 이게 최선의 일반해.

## Complexity

- 시간: **O(n log n)** — 정렬이 지배, 이후 순회는 O(n).
- 공간: **O(n)** — 결과 리스트 (겹침이 없으면 입력과 같은 크기) + 정렬 부가 공간.

## Solution (Python)

```python
from typing import List


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []

    intervals_sorted = sorted(intervals, key=lambda iv: iv[0])  # O(n log n)

    merged = [intervals_sorted[0][:]]
    for start, end in intervals_sorted[1:]:                     # O(n)
        last = merged[-1]
        if start <= last[1]:          # 겹치거나 맞닿음
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged


if __name__ == "__main__":
    print(merge_intervals([[5, 8], [1, 3], [2, 4], [10, 12]]))
    # [[1, 4], [5, 8], [10, 12]]
```

## Solution (Java)

```java
import java.util.*;

public class BookingConsolidation {

    public static int[][] mergeIntervals(int[][] intervals) {
        if (intervals.length == 0) {
            return new int[0][];
        }

        int[][] sorted = intervals.clone();
        Arrays.sort(sorted, (a, b) -> Integer.compare(a[0], b[0])); // O(n log n)

        List<int[]> merged = new ArrayList<>();
        merged.add(sorted[0].clone());

        for (int i = 1; i < sorted.length; i++) {                  // O(n)
            int[] last = merged.get(merged.size() - 1);
            int start = sorted[i][0];
            int end = sorted[i][1];
            if (start <= last[1]) {
                last[1] = Math.max(last[1], end);
            } else {
                merged.add(sorted[i].clone());
            }
        }

        return merged.toArray(new int[0][]);
    }

    public static void main(String[] args) {
        int[][] result = mergeIntervals(new int[][]{{5, 8}, {1, 3}, {2, 4}, {10, 12}});
        for (int[] interval : result) {
            System.out.println(Arrays.toString(interval));
        }
        // [1, 4]
        // [5, 8]
        // [10, 12]
    }
}
```

## Verification

파이썬 구현을 실행해 `[[5,8],[1,3],[2,4],[10,12]]` → `[[1,4],[5,8],[10,12]]`,
맞닿는 케이스 `[[1,4],[4,5]]` → `[[1,5]]`를 확인했다.
