---
id: shifted-frequency-report
title: Shifted Frequency Report
category: strings-hashing
difficulty: medium
trigger: "per-character transform, then a frequency-based report per distinct char"
pattern: "single pass + hashmap counting"
time_target_min: 15
---

## Problem

A legacy logging system obfuscates each record before analysis. Given a string
`s` of length `n` (letters, digits, spaces, and punctuation), produce its
"frequency report" in three steps:

1. **Shift**: replace every alphanumeric character with the previous character
   in its sequence, wrapping around: `b -> a`, `B -> A`, `1 -> 0`, and at the
   boundaries `a -> z`, `A -> Z`, `0 -> 9`. Spaces and punctuation are left
   unchanged.
2. **Count**: in the shifted string, count how many times each alphanumeric
   character appears.
3. **Report**: for every distinct character that appeared, compute
   `|ASCII value - count|`, then return these values sorted in ascending
   order.

## Examples

Input: `"Data 42!"`
Shifted: `"Czsz 31!"` (D->C, a->z wraps, t->s, a->z, 4->3, 2->1)
Counts: `{C:1, z:2, s:1, 3:1, 1:1}`
Differences: `|67-1|=66, |122-2|=120, |115-1|=114, |51-1|=50, |49-1|=48`
Output: `[48, 50, 66, 114, 120]`

## Constraints

- `1 <= n <= 500`; characters are ASCII letters, digits, spaces, punctuation.
- Distinct alphanumeric characters are at most 62 (a-z, A-Z, 0-9).

## Approach

- 시프트는 문자 하나당 O(1) (분기 4개: a/A/0 랩어라운드, 일반 영숫자, 비영숫자).
- 빈도 계산은 해시맵(파이썬 dict/Counter, 자바 HashMap)으로 O(n).
- "등장한 문자 종류" 수는 최대 62개로 고정 상한이 있으므로, 차이값 리스트 정렬은
  사실상 O(62 log 62) = 상수. 일반화하면 O(k log k) (k = 고유 문자 수, k <= 62).

## Complexity

- 시간: **O(n)** — 시프트 O(n) + 빈도 집계 O(n) + 정렬 O(k log k) (k <= 62라 상수 취급).
- 공간: **O(1)** 부가 공간 (입력 저장 제외; 카운트 맵이 최대 62 엔트리).

## Solution (Python)

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

    shifted = ''.join(shift(c) for c in s)                 # O(n)
    freq = Counter(c for c in shifted if c.isalnum())      # O(n)

    diffs = [abs(ord(ch) - cnt) for ch, cnt in freq.items()]  # O(k), k <= 62
    diffs.sort()                                           # O(k log k)
    return diffs


if __name__ == "__main__":
    print(encode_and_diff("Data 42!"))
    # [48, 50, 66, 114, 120]
```

## Solution (Java)

```java
import java.util.*;

public class ShiftedFrequencyReport {

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
            diffs.add(Math.abs((int) e.getKey() - e.getValue()));
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
        System.out.println(encodeAndDiff("Data 42!"));
        // [48, 50, 66, 114, 120]
    }
}
```

## Verification

파이썬 코드를 실제로 실행해 `"Data 42!"` → 시프트 `"Czsz 31!"` →
`[48, 50, 66, 114, 120]`이 나오는 것을 확인했다.
