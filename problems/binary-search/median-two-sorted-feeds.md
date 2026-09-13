---
id: median-two-sorted-feeds
title: Median of Two Sorted Feeds
category: binary-search
difficulty: hard
trigger: "median (or k-th element) of TWO sorted arrays without merging, in log time"
pattern: "binary search the partition of the smaller array; cross-check left-max <= right-min"
time_target_min: 25
---

## Problem

Two monitoring servers each keep their latency samples in a sorted list.
Implement `combined_median(nums1, nums2)` that returns the median of all
samples combined, in **O(log(min(m, n)))** time. Actually merging the two
lists (O(m + n)) is not accepted. Either list may be empty (but not both).

Return the median as a float: for an odd total count, the middle value; for
an even total count, the average of the two middle values.

## Examples

Input: `nums1 = [2, 6]`, `nums2 = [4]` → Output: `4.0`
(combined: [2, 4, 6])

Input: `nums1 = [1, 5]`, `nums2 = [2, 8]` → Output: `3.5`
(combined: [1, 2, 5, 8] → (2 + 5) / 2)

Input: `nums1 = []`, `nums2 = [3, 7]` → Output: `5.0`

## Constraints

- `0 <= m, n <= 10^5`, `m + n >= 1`, both lists individually sorted.
- Required: O(log(min(m, n))) time — merging or two-pointer counting is O(m+n).

## Approach

중앙값의 정의를 바꿔 말하면: **합친 배열의 "왼쪽 절반"에 정확히
`(m + n + 1) // 2`개가 들어가도록 두 배열을 각각 자르는 방법**을 찾는 것.

- nums1에서 `i`개, nums2에서 `j = (m+n+1)//2 - i`개를 왼쪽에 넣는다고 하자.
- 이 분할이 올바르려면 **교차 조건**만 확인하면 된다:
  `nums1 왼쪽의 최대(left1) <= nums2 오른쪽의 최소(right2)` 그리고
  `nums2 왼쪽의 최대(left2) <= nums1 오른쪽의 최소(right1)`.
  (각 배열 내부는 이미 정렬돼 있으니 검사할 필요가 없다.)
- 조건이 깨지는 방향이 곧 이분 탐색의 방향: `left1 > right2`면 nums1에서
  너무 많이 가져온 것 → i를 줄인다. 반대면 늘린다. **i에 대해 단조**라서
  이분 탐색이 성립한다.
- 찾으면: 홀수 총합 → `max(left1, left2)`, 짝수 →
  `(max(left1, left2) + min(right1, right2)) / 2`.

**왜 작은 배열에서 탐색하는가**: 탐색 범위가 O(log min)이 되고, i의 범위
[0, m]에서 j가 항상 음수가 아니게 보장된다 (큰 배열에서 탐색하면 j가 범위를
벗어날 수 있음).

**구현 실수의 대부분은 경계 처리**: 분할이 배열의 맨 앞(0개)이나 맨 뒤(전부)에
올 때 비교 대상이 없어지는데, `±inf` 센티널로 통일하면 분기 없이 처리된다.
빈 배열(m=0)도 같은 방식으로 자연스럽게 커버된다.

## Complexity

- 시간: **O(log(min(m, n)))** — 작은 배열에 대한 이분 탐색.
- 공간: **O(1)**.

## Solution (Python)

```python
def combined_median(nums1, nums2):
    # Always binary-search the smaller array
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    left, right = 0, m

    while left <= right:
        # Partition nums1; partition nums2 so the left side holds half
        partition1 = (left + right) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # Values immediately around the partitions (±inf sentinels
        # make the 0-elements / all-elements edges branch-free)
        left1 = float("-inf") if partition1 == 0 else nums1[partition1 - 1]
        right1 = float("inf") if partition1 == m else nums1[partition1]
        left2 = float("-inf") if partition2 == 0 else nums2[partition2 - 1]
        right2 = float("inf") if partition2 == n else nums2[partition2]

        # Correct partition found
        if left1 <= right2 and left2 <= right1:
            if (m + n) % 2 == 1:
                return float(max(left1, left2))
            return (max(left1, left2) + min(right1, right2)) / 2.0
        elif left1 > right2:      # took too many from nums1
            right = partition1 - 1
        else:                     # took too few from nums1
            left = partition1 + 1

    return 0.0  # unreachable for valid sorted input


if __name__ == "__main__":
    print(combined_median([2, 6], [4]))        # 4.0
    print(combined_median([1, 5], [2, 8]))     # 3.5
    print(combined_median([], [3, 7]))         # 5.0
    print(combined_median([10], [1, 2, 3, 4])) # 3.0
```

## Solution (Java)

```java
public class MedianTwoSortedFeeds {

    public static double combinedMedian(int[] nums1, int[] nums2) {
        if (nums1.length > nums2.length) {
            return combinedMedian(nums2, nums1);
        }
        int m = nums1.length, n = nums2.length;
        int left = 0, right = m;

        while (left <= right) {
            int p1 = (left + right) / 2;
            int p2 = (m + n + 1) / 2 - p1;

            int left1 = (p1 == 0) ? Integer.MIN_VALUE : nums1[p1 - 1];
            int right1 = (p1 == m) ? Integer.MAX_VALUE : nums1[p1];
            int left2 = (p2 == 0) ? Integer.MIN_VALUE : nums2[p2 - 1];
            int right2 = (p2 == n) ? Integer.MAX_VALUE : nums2[p2];

            if (left1 <= right2 && left2 <= right1) {
                if ((m + n) % 2 == 1) {
                    return Math.max(left1, left2);
                }
                return (Math.max(left1, left2) + Math.min(right1, right2)) / 2.0;
            } else if (left1 > right2) {
                right = p1 - 1;
            } else {
                left = p1 + 1;
            }
        }
        return 0.0; // unreachable for valid sorted input
    }

    public static void main(String[] args) {
        System.out.println(combinedMedian(new int[]{2, 6}, new int[]{4}));    // 4.0
        System.out.println(combinedMedian(new int[]{1, 5}, new int[]{2, 8})); // 3.5
    }
}
```

## Verification

파이썬 구현을 실행해 5개 케이스(홀수/짝수 총합, 빈 배열, 길이 불균형
`[10]` vs `[1,2,3,4]`, 중복값 `[1,1]`+`[1,1]`)를
`statistics.median(sorted(a+b))` 브루트포스와 대조해 전부 일치함을 확인했다.

관련 플래시카드: card-median-partition, card-binary-search-answer.
