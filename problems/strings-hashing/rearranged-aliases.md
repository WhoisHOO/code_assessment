---
id: rearranged-aliases
title: Rearranged Aliases
category: strings-hashing
difficulty: medium
trigger: "group strings that are rearrangements (anagrams) of one another"
pattern: "canonical frequency key + hashmap of groups"
time_target_min: 15
---

## Problem

A moderation tool flags usernames that are rearrangements of each other
(same letters with the same counts, in any order) as aliases of one account.
Write a function `group_aliases(names)` that takes a list of lowercase
strings and returns a list of groups, where each group contains all strings
that are rearrangements of one another.

The order of the groups, and of the strings within a group, does not matter.

## Examples

Input: `["care", "race", "acre", "note", "tone", "leaf"]`
Output: `[["care", "race", "acre"], ["note", "tone"], ["leaf"]]`
("care", "race", "acre" all use a/c/e/r once; "note"/"tone" use e/n/o/t once.)

## Constraints

- `1 <= names.length <= 10^4`
- `0 <= names[i].length <= 100`
- `names[i]` consists of lowercase English letters only.
- Brute-force pairwise comparison of every pair is not accepted — aim for a
  single pass over the input.

## Approach

핵심은 **"재배열이면 같아지는 canonical key"를 만들어서 해시맵의 키로 쓰는 것**:

```
count = [0] * 26
for char in s:
    count[ord(char) - ord('a')] += 1
key = tuple(count)
```

예를 들어 "care"와 "race"는 순서가 다르지만 둘 다 a, c, e, r가 한 번씩이므로
**똑같은 key**가 만들어진다. 따라서 dictionary가 자동으로 같은 그룹에 넣어준다.

- 대안 key: 각 문자열을 정렬한 문자열 (`''.join(sorted(s))`). 문자열당
  O(k log k)라 빈도 배열(O(k))보다 느리지만 구현이 짧다. 알파벳이 26자로
  고정이라는 제약 덕에 빈도 배열이 가능한 것.
- 브루트포스(모든 쌍 비교)는 O(n^2 · k)라 n = 10^4에서 탈락.

## Complexity

- 시간: **O(n · k)** — n = 문자열 수, k = 최대 문자열 길이. 문자열마다 빈도
  배열 한 번(O(k)) + key 생성 O(26).
- 공간: **O(n · 26)** — 그룹 맵의 key들 (결과 저장 제외 시 문자열당 26칸 배열).

## Solution (Python)

```python
from typing import List


def group_aliases(names: List[str]) -> List[List[str]]:
    groups = {}

    for s in names:
        # Count the frequency of each letter
        count = [0] * 26
        for char in s:
            count[ord(char) - ord('a')] += 1

        # Rearrangements share the same character-frequency pattern
        key = tuple(count)
        groups.setdefault(key, []).append(s)

    return list(groups.values())


if __name__ == "__main__":
    print(group_aliases(["care", "race", "acre", "note", "tone", "leaf"]))
    # [['care', 'race', 'acre'], ['note', 'tone'], ['leaf']]
```

## Solution (Java)

```java
import java.util.*;

public class RearrangedAliases {

    public static List<List<String>> groupAliases(String[] names) {
        Map<String, List<String>> groups = new HashMap<>();

        for (String s : names) {
            int[] count = new int[26];
            for (char c : s.toCharArray()) {
                count[c - 'a']++;
            }
            // Arrays.toString gives a stable canonical key like "[1, 0, 1, ...]"
            String key = Arrays.toString(count);
            groups.computeIfAbsent(key, k -> new ArrayList<>()).add(s);
        }

        return new ArrayList<>(groups.values());
    }

    public static void main(String[] args) {
        System.out.println(groupAliases(
            new String[]{"care", "race", "acre", "note", "tone", "leaf"}));
        // [[care, race, acre], [note, tone], [leaf]]
    }
}
```

## Verification

파이썬 구현을 실행해 예시 입력 →
`[['care', 'race', 'acre'], ['note', 'tone'], ['leaf']]`,
빈 문자열 케이스 `['', '', 'a']` → `[['', ''], ['a']]`를 확인했다
(빈 문자열끼리도 같은 key라 한 그룹).

관련 플래시카드: card-string-frequency (frequency count as canonical key).
