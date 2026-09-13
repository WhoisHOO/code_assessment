---
id: corridor-hops
title: Corridor Hops
category: dynamic-programming
difficulty: easy
trigger: "count the ways to reach position n when each move advances 1 or 2"
pattern: "1D DP (Fibonacci recurrence), two rolling variables"
time_target_min: 10
---

## Problem

A robot starts at position 0 in a corridor of `n` tiles. In one move it hops
forward either 1 tile or 2 tiles. Count how many distinct sequences of moves
land the robot exactly on tile `n`. Solve it with **dynamic programming** —
enumerating every path (brute force) is not accepted.

## Examples

Input: `n = 5`
Output: `8`
(The 8 sequences: 1+1+1+1+1, 1+1+1+2, 1+1+2+1, 1+2+1+1, 2+1+1+1, 1+2+2,
2+1+2, 2+2+1.)

## Constraints

- `0 <= n <= 45` (the answer fits in a 32-bit signed int in this range).
- Target: O(n) time, O(1) extra space.

## Approach

n번 타일에 도달하는 마지막 이동은 "1칸 홉" 아니면 "2칸 홉" 둘 중 하나뿐이다.

- 마지막이 1칸이었다면 직전엔 n-1까지 온 것 → `ways(n-1)`가지
- 마지막이 2칸이었다면 직전엔 n-2까지 온 것 → `ways(n-2)`가지

두 경우는 겹치지 않으므로:

```
ways(n) = ways(n-1) + ways(n-2)
ways(0) = 1   (아무것도 안 움직이는 방법 1가지 — 이미 도착)
ways(1) = 1
```

피보나치 수열과 동일한 점화식. 브루트포스(재귀로 모든 경로 나열)는 같은 부분
문제를 지수적으로 중복 계산해 O(2^n)이 되므로, 이전 두 값만 기억하는
**상향식(bottom-up) DP**로 O(n)에 푼다 — 배열 없이 변수 두 개(rolling
variables)면 충분하다.

## Complexity

- 시간: **O(n)** — 2부터 n까지 한 번씩만 계산.
- 공간: **O(1)** — 직전 두 값만 변수로 유지. 전체 DP 테이블을 저장하면 O(n)이지만
  이 문제는 `ways(n-1)`, `ways(n-2)`만 필요하다.

## Solution (Python)

```python
def total_ways(n: int) -> int:
    if n <= 1:
        return 1
    prev2, prev1 = 1, 1  # ways(0), ways(1)
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1


if __name__ == "__main__":
    print(total_ways(5))  # 8
```

## Solution (Java)

```java
public class CorridorHops {
    public static int totalWays(int n) {
        if (n <= 1) {
            return 1;
        }
        int prev2 = 1; // ways(0)
        int prev1 = 1; // ways(1)
        for (int i = 2; i <= n; i++) {
            int curr = prev1 + prev2;
            prev2 = prev1;
            prev1 = curr;
        }
        return prev1;
    }

    public static void main(String[] args) {
        System.out.println(totalWays(5)); // 8
    }
}
```

## Verification

파이썬 코드를 n=0..6에 대해 실행해 `1, 1, 2, 3, 5, 8, 13`을 확인했다
(피보나치 수열과 일치, n=5일 때 8).
