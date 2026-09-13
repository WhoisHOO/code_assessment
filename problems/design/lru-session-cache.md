---
id: lru-session-cache
title: LRU Session Cache
category: design
difficulty: medium
trigger: "O(1) lookup AND O(1) recency reordering/eviction (design an LRU cache)"
pattern: "hashmap of key -> node + doubly linked list with dummy head/tail"
time_target_min: 20
---

## Problem

A web service caches at most `capacity` session records in memory. Design a
Least Recently Used (LRU) cache supporting both operations in **O(1)**
average time:

- `get(key)`: return the key's value if present, else `-1`. A successful get
  counts as a "use" and makes the key the most recently used.
- `put(key, value)`: insert, or update an existing key's value (an update
  also counts as a use). If the insertion pushes the cache past `capacity`,
  evict the least recently used key.

Implement a class with `__init__(self, capacity)`, `get(self, key) -> int`,
and `put(self, key, value) -> None`.

## Examples

```
cache = LRUCache(2)
cache.put(10, 100)
cache.put(20, 200)
cache.get(20)      # 200; 20 is now most recently used (LRU is 10)
cache.put(30, 300) # over capacity -> evicts 10
cache.get(10)      # -1
cache.get(20)      # 200
cache.put(20, 250) # updates value in place; 20 becomes MRU again
cache.put(40, 400) # evicts 30 (20 was used more recently)
cache.get(30)      # -1
cache.get(20)      # 250
cache.get(40)      # 400
```

## Constraints

- `1 <= capacity <= 3000`, `0 <= key, value <= 10^4`
- Up to `2 * 10^5` combined calls to get/put. Both must be O(1) average.

## Approach

**왜 자료구조가 두 개 필요한가** — 이 문제의 진짜 내용:

- dict만 쓰면 `key → value` 조회는 O(1)이지만 "가장 오래 안 쓰인 key가
  누구인가"의 **순서 관리**가 안 된다.
- 연결 리스트만 쓰면 LRU→MRU 순서 유지와 노드 이동은 쉽지만, `get(key)`때
  노드를 **찾는 것**이 O(n)이다.
- 그래서 합친다: **HashMap(key → Node) + Doubly Linked List(사용 순서)**.
  맵으로 노드를 O(1)에 찾고, 찾은 노드를 리스트에서 O(1)에 떼어 MRU 끝으로
  옮긴다. 떼어내기가 O(1)이려면 prev 포인터가 필요하므로 **doubly** linked
  list여야 한다 (singly면 이전 노드를 찾는 데 O(n)).

면접관이 확인하려는 사고 회로: "O(1) lookup 필요" → HashMap, "O(1)
제거/재배치 필요" → DLL, "둘 다" → 결합.

구현 디테일 세 가지가 당락을 가른다:

1. **더미 head/tail 노드** — `left`(LRU쪽), `right`(MRU쪽) 더미를 두면
   빈 리스트/끝 삽입/맨 앞 제거의 null 분기가 전부 사라진다.
2. **Node에 key도 저장** — 용량 초과로 LRU 노드를 리스트에서 떼어낸 뒤
   `del self.cache[lru.key]`를 해야 하는데, value만 저장하면 dict에서 뭘
   지울지 알 수 없다.
3. get과 put(기존 key)은 둘 다 "사용"이므로 remove + insert로 MRU 이동.

## Complexity

- 시간: get/put 모두 **O(1)** — dict 조회 + 포인터 조작 상수 회.
- 공간: **O(capacity)** — 맵 + 리스트 노드.

## Solution (Python)

```python
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}          # key -> Node

        # dummy nodes: left = LRU side, right = MRU side
        self.left = Node()
        self.right = Node()
        self.left.next = self.right
        self.right.prev = self.left

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert(self, node):
        # insert right before the right dummy = most recently used
        prev_node = self.right.prev
        prev_node.next = node
        node.prev = prev_node
        node.next = self.right
        self.right.prev = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)       # a get is a "use":
        self._insert(node)       # move to the MRU position
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._insert(node)
        else:
            node = Node(key, value)
            self.cache[key] = node
            self._insert(node)

        if len(self.cache) > self.capacity:
            lru = self.left.next          # first real node = LRU
            self._remove(lru)
            del self.cache[lru.key]       # this is why Node stores its key
```

실전 지름길: 파이썬은 `collections.OrderedDict`로 같은 O(1)을 훨씬 짧게
쓸 수 있다 (`move_to_end(key)` + `popitem(last=False)`). 자동 채점이면
이걸로 시간을 아끼고, 사람이 보는 면접이면 위 수동 구현을 요구받을 수 있으니
둘 다 알아둘 것.

## Solution (Java)

```java
import java.util.*;

public class LRUCache {

    private static class Node {
        int key, value;
        Node prev, next;
        Node(int key, int value) { this.key = key; this.value = value; }
    }

    private final int capacity;
    private final Map<Integer, Node> cache = new HashMap<>();
    private final Node left = new Node(0, 0);   // LRU side dummy
    private final Node right = new Node(0, 0);  // MRU side dummy

    public LRUCache(int capacity) {
        this.capacity = capacity;
        left.next = right;
        right.prev = left;
    }

    private void remove(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void insert(Node node) {
        Node prevNode = right.prev;
        prevNode.next = node;
        node.prev = prevNode;
        node.next = right;
        right.prev = node;
    }

    public int get(int key) {
        Node node = cache.get(key);
        if (node == null) return -1;
        remove(node);
        insert(node);
        return node.value;
    }

    public void put(int key, int value) {
        Node node = cache.get(key);
        if (node != null) {
            node.value = value;
            remove(node);
            insert(node);
        } else {
            node = new Node(key, value);
            cache.put(key, node);
            insert(node);
        }
        if (cache.size() > capacity) {
            Node lru = left.next;
            remove(lru);
            cache.remove(lru.key);
        }
    }
}
```

자바 지름길: `LinkedHashMap`을 access-order 모드
(`new LinkedHashMap<>(cap, 0.75f, true)`)로 만들고 `removeEldestEntry`를
오버라이드하면 수동 DLL 없이 끝난다 — 역시 면접에서는 원리 설명을 요구받을
수 있다.

## Verification

파이썬 구현을 예시 시퀀스로 실행해 `200, -1, 200, -1, 250, 400`을 확인했다
(축출 2회, 기존 key 값 업데이트 후 MRU 갱신 케이스 포함).

관련 플래시카드: card-lru-design, card-heap-topk.
