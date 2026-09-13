---
id: profile-rainwater
title: Rainwater on an Elevation Profile
category: two-pointers-sliding-window
difficulty: hard
trigger: "1D bars/profile - how much water pools between them (each cell bounded by min of side maxima)"
pattern: "two pointers from both ends with running left_max/right_max - process the smaller side"
time_target_min: 20
---

## Problem

A retaining-wall survey records a cross-section as an array `profile` of
non-negative integers, where each value is a wall height of width 1.
Implement `pooled_water(profile: list[int]) -> int` that returns the total
amount of water the profile holds after rain, in **O(n) time and O(1) extra
space** (not counting the input).

(This is the 1D original of [[terrain-rainwater]] — the 2D grid version
where water can also escape sideways.)

## Examples

Input: `profile = [2, 0, 1, 0, 3]`
Output: `5` — the three middle cells fill to level `min(2, 3) = 2`:
(2-0) + (2-1) + (2-0) = 5.

Input: `profile = [3, 1, 2]` → Output: `1`
Input: `profile = [1, 2, 3]` → Output: `0` (monotonic slope holds nothing)

## Constraints

- `1 <= len(profile) <= 2 * 10^4`, `0 <= profile[i] <= 10^5`
- Required: O(n) time, O(1) extra space.

## Approach

**칸 하나의 물부터 정의한다**: 위치 i에 고이는 물 =
`min(왼쪽 전체의 최대 벽, 오른쪽 전체의 최대 벽) - profile[i]` (음수면 0).

- 매 칸마다 양쪽 최대를 새로 구하면 O(n²).
- 최대 벽을 배열 두 개(prefix-max, suffix-max)로 전처리하면 O(n) 시간이지만
  O(n) 공간 — 문제는 O(1) 공간을 요구한다.
- **Two pointers가 공간을 없앤다**: 양 끝에서 `left`, `right`를 좁혀 오면서
  `left_max`, `right_max`를 유지한다.

핵심 논리 한 줄 — **`profile[left] <= profile[right]`이면 왼쪽 칸은 지금
확정해도 된다**: 오른쪽에 현재 왼쪽 값 이상인 벽이 존재함을 방금 확인했으므로
왼쪽 칸의 수위는 `left_max`만으로 결정되고 (min이 왼쪽에서 걸림), 반대쪽
최대를 몰라도 된다. 반대 경우는 대칭으로 오른쪽 칸을 확정한다. 각 칸이
정확히 한 번 처리되므로 O(n).

확정 규칙: 현재 값이 자기 쪽 max 이상이면 max 갱신(벽), 아니면
`자기쪽 max - 현재 값`만큼 물 추가.

`[2,0,1,0,3]` 진행: 2<=3 → left_max=2 → 0: +2 → 1: +1 → 0: +2 → 합 5.

**2D로 가면 이 논리가 깨진다**: 물이 4방향으로 샐 수 있어 "반대쪽 경계가
충분히 높다"는 보장이 성립하지 않는다 → min-heap 경계 확장
([[terrain-rainwater]]). 두 문제를 쌍으로 기억할 것: 1D = two pointers,
2D = min-heap flood fill.

## Complexity

- 시간: **O(n)** — 각 인덱스를 한 번씩 처리.
- 공간: **O(1)** — 포인터 2개 + max 2개.

## Solution (Python)

```python
def pooled_water(profile: list[int]) -> int:
    if not profile:
        return 0

    left, right = 0, len(profile) - 1
    left_max = right_max = 0
    water = 0

    while left < right:
        if profile[left] <= profile[right]:
            # a wall >= profile[left] exists on the right,
            # so the water level here is decided by left_max alone
            if profile[left] >= left_max:
                left_max = profile[left]
            else:
                water += left_max - profile[left]
            left += 1
        else:
            if profile[right] >= right_max:
                right_max = profile[right]
            else:
                water += right_max - profile[right]
            right -= 1

    return water


if __name__ == "__main__":
    print(pooled_water([2, 0, 1, 0, 3]))  # 5
    print(pooled_water([3, 1, 2]))        # 1
    print(pooled_water([1, 2, 3]))        # 0
```

## Solution (Java)

```java
public class ProfileRainwater {

    public static int pooledWater(int[] profile) {
        int left = 0, right = profile.length - 1;
        int leftMax = 0, rightMax = 0;
        int water = 0;

        while (left < right) {
            if (profile[left] <= profile[right]) {
                if (profile[left] >= leftMax) {
                    leftMax = profile[left];
                } else {
                    water += leftMax - profile[left];
                }
                left++;
            } else {
                if (profile[right] >= rightMax) {
                    rightMax = profile[right];
                } else {
                    water += rightMax - profile[right];
                }
                right--;
            }
        }
        return water;
    }

    public static void main(String[] args) {
        System.out.println(pooledWater(new int[]{2, 0, 1, 0, 3}));  // 5
        System.out.println(pooledWater(new int[]{3, 1, 2}));        // 1
    }
}
```

## Verification

파이썬 구현을 실행해 확인: `[2,0,1,0,3]` → `5` (칸별
`min(prefix-max, suffix-max)` 브루트포스와 일치), `[3,1,2]` → `1`,
단조 증가 `[1,2,3]` → `0`, 단일 원소 → `0`.

관련 플래시카드: card-two-ends-maxima, card-two-pointers.
관련 문제: terrain-rainwater (2D 버전 — two pointers가 왜 못 가는지 포함).
