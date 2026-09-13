---
id: rearranged-aliases
title: Rearranged Aliases
category: strings-hashing
difficulty: medium
trigger: "group strings that are rearrangements (anagrams) of one another"
pattern: "canonical key (sorted string) + hashmap of groups"
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

핵심은 **"재배열이면 같아지는 canonical key"를 만들어서 해시맵의 키로 쓰는 것**.
key 전략이 두 가지 있고, 실전에서는 선택이 점수를 가른다:

**1) 정렬 키 (실전 기본값, 추천)** — `key = ''.join(sorted(s))`

- "care"와 "race"는 정렬하면 둘 다 "acer"가 되므로 같은 key.
- 문자열당 O(k log k)지만 **어떤 문자가 와도 동작한다** (대문자, 공백, 숫자,
  유니코드). 인덱스 산수가 없어서 시간 압박에서 실수할 여지도 없다.

**2) 빈도 배열 키 (조건부 최적화)** — `count[26]` 채워서 `tuple(count)`

- 문자열당 O(k)로 이론상 더 빠르다. 단, `ord(char) - ord('a')` 인덱스는
  **입력이 소문자 a-z뿐이라는 보장이 있을 때만 안전하다.**
- ⚠ 실패 모드: 히든 테스트에 대문자/공백/숫자가 하나라도 있으면
  `ord('A') - ord('a') = -32` 같은 음수 인덱스가 나와 **IndexError로 즉사**한다.
  "이론상 최적"이 런타임 에러로 0점이 되는 전형적 사례. 제약 조건에
  "lowercase only"가 명시돼 있는지 확인한 경우에만 쓸 것.

n = 10^4, k <= 100이면 k log k vs k 차이는 체감 불가 — 정렬 키로 충분하다.
브루트포스(모든 쌍 비교)는 O(n^2 · k)라 탈락.

## Complexity

- 시간: **O(n · k log k)** (정렬 키) / O(n · k) (빈도 배열 키).
  n = 문자열 수, k = 최대 문자열 길이.
- 공간: **O(n · k)** — 그룹 맵의 key + 결과 저장.

## Solution (Python)

```python
from collections import defaultdict
from typing import List


def group_aliases(names: List[str]) -> List[List[str]]:
    groups = defaultdict(list)

    for s in names:
        # Rearrangements sort to the identical string -> same key.
        # Works for ANY characters; no index arithmetic to get wrong.
        key = ''.join(sorted(s))
        groups[key].append(s)

    return list(groups.values())


if __name__ == "__main__":
    print(group_aliases(["care", "race", "acre", "note", "tone", "leaf"]))
    # [['care', 'race', 'acre'], ['note', 'tone'], ['leaf']]
```

빈도 배열 최적화 버전 (소문자 보장이 확인된 경우에만):

```python
def group_aliases_counted(names: List[str]) -> List[List[str]]:
    groups = defaultdict(list)
    for s in names:
        count = [0] * 26
        for char in s:
            count[ord(char) - ord('a')] += 1  # a-z 외 문자가 오면 IndexError!
        groups[tuple(count)].append(s)
    return list(groups.values())
```

## Solution (Java)

```java
import java.util.*;

public class RearrangedAliases {

    public static List<List<String>> groupAliases(String[] names) {
        Map<String, List<String>> groups = new HashMap<>();

        for (String s : names) {
            char[] chars = s.toCharArray();
            Arrays.sort(chars);                 // canonical key, any charset
            String key = new String(chars);
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

정렬 키 구현을 실행해 예시 입력 →
`[['care', 'race', 'acre'], ['note', 'tone'], ['leaf']]`,
빈 문자열 케이스 `['', '', 'a']` → `[['', ''], ['a']]`,
혼합 문자 `['Care', 'race', 'a1 b', 'b a1']` →
`[['Care'], ['race'], ['a1 b', 'b a1']]` (크래시 없음)을 확인했다.
빈도 배열 버전은 소문자 입력에서 동일 결과를 내는 것을 확인했다.

## Post-mortem notes

- 2026-09-13 실전 기록: 빈도 배열 풀이가 플랫폼 채점에서 실행 에러 —
  히든 테스트에 소문자 외 문자가 있었을 가능성이 가장 높다 (음수 인덱스 →
  IndexError). 교훈: **제약을 내가 통제 못 하는 채점 환경에서는 가정이 적은
  풀이가 최선의 답이다.** 최적화는 제약 문구를 확인한 뒤에.

관련 플래시카드: card-string-frequency (frequency count as canonical key).
