# Coding Problems — 문제 정리와 풀이

여러 코딩 문제를 문제별로 정리한다. 새 문제가 생기면 아래 "문제 N" 형식으로 이어서 추가한다.

---

## 문제 1. Bob's String Encoding

### 문제 요약

길이 n(1 ≤ n ≤ 500)인 문자열(영숫자 + 공백/구두점)이 주어진다.

1. **시프트**: 각 영숫자 문자를 시퀀스상 "이전 문자"로 바꾼다.
   - 알파벳: b→a, B→A ... / wrap: a→z, A→Z
   - 숫자: 1→0, 2→1 ... / wrap: 0→9
   - 공백·구두점은 그대로 둔다.
2. **빈도 계산**: 시프트된 문자열에서 영숫자 문자별 등장 횟수를 센다.
3. **차이 계산**: 등장한 문자마다 `|ASCII값 - 빈도수|`를 구한다.
4. 이 차이값들을 오름차순 정렬해서 리스트로 반환한다.

예시 `"Hello, 123!"` → 시프트 `"Gdkkn, 012!"` → 빈도 `{G:1, d:1, k:2, n:1, 0:1, 1:1, 2:1}`
→ 차이 `[70, 99, 105, 109, 47, 48, 49]` → 정렬 `[47, 48, 49, 70, 99, 105, 109]`

### 접근 방식

- 시프트는 문자 하나당 O(1) (분기 4개: a/A/0/일반/비영숫자).
- 빈도 계산은 해시맵(파이썬 dict / 자바 HashMap)으로 O(n).
- "등장한 문자 종류" 수는 최대 62개(a-z, A-Z, 0-9)로 상수 개념에 가까우므로,
  차이값 리스트 정렬은 사실상 O(62 log 62) = O(1)이지만 일반화해서 O(k log k)(k = 등장한 고유 문자 수, k ≤ 62)로 표기.

### 시간/공간 복잡도

**O(n)** — n은 입력 문자열 길이.

- 시프트: O(n)
- 빈도 집계: O(n)
- 정렬: O(k log k), k ≤ 62 → 사실상 상수, 전체 복잡도를 지배하지 않음
- 공간: O(k) ≤ O(62) = O(1) (입력 자체를 저장하는 O(n)을 빼면 부가 공간은 상수)

→ **전체: 시간 O(n), 부가 공간 O(1)** (문자 종류 수가 62로 고정 상한이 있기 때문)

### 파이썬 풀이

```python
from collections import Counter

def encode_and_diff(s: str) -> list[int]:
    def shift(c: str) -> str:
        if c == 'a':
            return 'z'
        if c == 'A':
            return 'Z'
        if c == '0':
            return '9'
        if c.isalnum():
            return chr(ord(c) - 1)
        return c  # 공백/구두점은 그대로

    shifted = ''.join(shift(c) for c in s)          # O(n)
    freq = Counter(c for c in shifted if c.isalnum())  # O(n)

    diffs = [abs(ord(ch) - cnt) for ch, cnt in freq.items()]  # O(k), k <= 62
    diffs.sort()                                     # O(k log k)
    return diffs


if __name__ == "__main__":
    print(encode_and_diff("Hello, 123!"))
    # [47, 48, 49, 70, 99, 105, 109]
```

### 자바 풀이

```java
import java.util.*;

public class BobStringEncoding {

    public static List<Integer> encodeAndDiff(String s) {
        StringBuilder shifted = new StringBuilder(s.length());
        for (char c : s.toCharArray()) {
            shifted.append(shift(c));
        }

        Map<Character, Integer> freq = new HashMap<>();
        for (char c : shifted.toString().toCharArray()) {
            if (Character.isLetterOrDigit(c)) {
                freq.merge(c, 1, Integer::sum);
            }
        }

        List<Integer> diffs = new ArrayList<>();
        for (Map.Entry<Character, Integer> e : freq.entrySet()) {
            int ascii = (int) e.getKey();
            int count = e.getValue();
            diffs.add(Math.abs(ascii - count));
        }

        Collections.sort(diffs);
        return diffs;
    }

    private static char shift(char c) {
        if (c == 'a') return 'z';
        if (c == 'A') return 'Z';
        if (c == '0') return '9';
        if (Character.isLetterOrDigit(c)) {
            return (char) (c - 1);
        }
        return c; // 공백/구두점 그대로
    }

    public static void main(String[] args) {
        System.out.println(encodeAndDiff("Hello, 123!"));
        // [47, 48, 49, 70, 99, 105, 109]
    }
}
```

### 검증

파이썬 코드를 실제로 실행해 예시 입력 `"Hello, 123!"`에 대해
`[47, 48, 49, 70, 99, 105, 109]`가 나오는 것을 확인했다 (문제 예시와 동일).

---

## 문제 2. Climbing Stairs

### 문제 요약

계단 n개를 오른다(0번 계단에서 시작). 매 스텝마다 1칸 또는 2칸을 오를 수 있다.
n칸을 오르는 서로 다른 방법의 총 개수를 **동적 계획법**으로 구한다 (브루트포스 금지).

예시: n=4 → 4 = 1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2 → 총 5가지.

### 접근 방식

n칸에 도달하는 마지막 스텝은 "1칸짜리 스텝" 아니면 "2칸짜리 스텝" 둘 중 하나뿐이다.

- 마지막이 1칸 스텝이었다면, 그 직전엔 n-1칸까지 온 것 → `ways(n-1)`가지
- 마지막이 2칸 스텝이었다면, 그 직전엔 n-2칸까지 온 것 → `ways(n-2)`가지

이 두 경우는 겹치지 않으므로:

```
ways(n) = ways(n-1) + ways(n-2)
ways(0) = 1   (아무것도 안 오르는 방법 1가지 — 이미 도착)
ways(1) = 1   (1칸만 오르는 방법 1가지)
```

피보나치 수열과 동일한 점화식이다. 브루트포스(재귀로 모든 경로 나열)는 같은 부분 문제를
지수적으로 중복 계산해 O(2^n)이 되므로, 이전 두 값만 기억하는 **상향식(bottom-up) DP**로
O(n)에 푼다 — 배열 전체를 저장할 필요도 없이 변수 두 개(rolling variables)면 충분하다.

### 시간/공간 복잡도

- **시간: O(n)** — 2부터 n까지 한 번씩만 계산.
- **공간: O(1)** — 배열 대신 직전 두 값만 변수로 유지(스페이스 최적화 버전).
  전체 DP 테이블을 저장하면 O(n) 공간이지만, 이 문제는 `ways(n-1)`, `ways(n-2)` 두 값만
  필요하므로 O(1)로 충분하다.

### 자바 풀이

```java
public class Solution {
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
        System.out.println(totalWays(4)); // 5
    }
}
```

### 파이썬 풀이

```python
def total_ways(n: int) -> int:
    if n <= 1:
        return 1
    prev2, prev1 = 1, 1  # ways(0), ways(1)
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1


if __name__ == "__main__":
    print(total_ways(4))  # 5
```

### 검증

파이썬 코드를 n=0..7에 대해 직접 실행해 `1, 1, 2, 3, 5, 8, 13, 21`을 확인했다
(피보나치 수열과 일치, n=4일 때 문제 예시와 동일하게 5가 나옴).

---

## 문제 3. Merge Intervals

### 문제 요약

정렬되지 않은 구간 리스트 `[start, end]`가 주어진다. 겹치는 구간들을 전부 합쳐서,
겹치지 않는 구간들의 리스트를 **시작 시각 기준 오름차순**으로 반환한다.

예시: `[[1,3],[2,6],[8,10],[15,18]]` → `[1,3]`과 `[2,6]`이 겹치므로 `[1,6]`으로 합쳐져
`[[1,6],[8,10],[15,18]]`을 반환.

제약: 각 구간은 `start <= end`. 빈 리스트가 들어오면 빈 리스트를 반환.
목표 복잡도: 정렬 후 한 번의 순회로 **O(n log n)**.

### 접근 방식

1. **시작 시각 기준으로 정렬**한다. 정렬해두면 "지금 보고 있는 구간이 이전에 합쳐둔
   구간과 겹치는지"만 확인하면 되므로, 뒤쪽에 있던 구간이 앞쪽 구간과 겹치는지
   따로 되짚어볼 필요가 없어진다 (정렬이 문제를 1차원 순회로 바꿔준다).
2. 결과 리스트를 유지하면서, 정렬된 구간을 하나씩 본다:
   - 결과 리스트의 **마지막 구간의 end**보다 현재 구간의 **start가 작거나 같으면**
     겹친다(또는 맞닿는다, 예: `[1,4]`와 `[4,5]`) → 마지막 구간의 end를
     `max(마지막.end, 현재.end)`로 갱신 (현재 구간이 마지막 구간에 완전히 포함되는
     경우, 예: `[1,4]`와 `[2,3]`도 이 max로 자연스럽게 처리됨).
   - 겹치지 않으면 현재 구간을 새 구간으로 결과 리스트에 추가한다.
3. 정렬이 끝난 상태이므로 결과는 이미 시작 시각 기준 오름차순이다.

버킷 정렬 등으로 O(n)에 더 빠르게 하는 방법도 있지만, 구간 값의 범위에 제약이 없는
일반적인 경우 비교 기반 정렬의 하한이 O(n log n)이라 이게 최선의 일반해다.

### 시간/공간 복잡도

- **시간: O(n log n)** — 정렬이 O(n log n), 이후 단일 순회가 O(n)이므로 정렬이 지배.
- **공간: O(n)** — 결과 리스트(최악의 경우 겹치는 구간이 없으면 입력과 같은 크기)
  + 정렬 자체가 쓰는 부가 공간(Timsort/Java Collections.sort 기준 O(n) 또는 O(log n),
  구현체에 따라 다름).

### 파이썬 풀이

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
    print(merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]))
    # [[1, 6], [8, 10], [15, 18]]
```

### 자바 풀이

```java
import java.util.*;

public class MergeIntervals {

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
        int[][] result = mergeIntervals(new int[][]{{1, 3}, {2, 6}, {8, 10}, {15, 18}});
        for (int[] interval : result) {
            System.out.println(Arrays.toString(interval));
        }
        // [1, 6]
        // [8, 10]
        // [15, 18]
    }
}
```

### 검증

문제에 포함된 `run_tests()` 하네스(테스트 7개: 부분 겹침, 맞닿음, 완전 포함, 겹침 없음,
빈 리스트, 단일 구간, 정렬 안 된 입력)로 파이썬 구현을 실행해 **7/7 전부 통과**를 확인했다.
