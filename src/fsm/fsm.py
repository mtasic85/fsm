import time
from typing import TypeAlias, Union, Optional, Any, Self
from collections.abc import Mapping, Callable, Awaitable


# Ctx: TypeAlias = Union[dict, Mapping]
Ctx: TypeAlias = dict

Res: TypeAlias = tuple[
    # Union[dict, Mapping, Awaitable[dict], Awaitable[Mapping]],
    Union[dict, Awaitable[dict]],
    Any,
]

RunFn: TypeAlias = Callable[[Ctx], Res]
ExcFn: TypeAlias = Callable[[Ctx, Exception], Res]


class Node:
    run_fn: RunFn
    exc_fn: ExcFn
    max_retries: int
    wait_time: float
    value_to_next_node: dict


    def __init__(self, run_fn: RunFn, exc_fn: ExcFn, max_retries: int=0, wait_time: Union[float, int]=5.0):
        self.run_fn = run_fn
        self.exc_fn = exc_fn
        self.max_retries = max_retries
        self.wait_time = float(wait_time)
        self.value_to_next_node = {}


    def __call__(self, ctx: Ctx, follow_next_node: bool = True) -> Res:
        current_node = self
        current_ctx = ctx

        while True:
            # Step 1: Execute current node with retries
            last_e = None
            res_ctx = None
            res_value = None

            # Retry loop for current node
            for attempt in range(current_node.max_retries + 1):
                try:
                    res_ctx, res_value = current_node.run_fn(current_ctx)
                    break
                except Exception as e:
                    last_e = e
                    if attempt < current_node.max_retries:
                        time.sleep(current_node.wait_time)
            else:
                # If all retries fail, use exc_fn
                res_ctx, res_value = current_node.exc_fn(current_ctx, last_e)

            # Step 2: Determine the next node based on the result
            next_node = current_node.value_to_next_node.get(res_value)

            # Step 3: Decide whether to continue traversal
            if not follow_next_node or next_node is None:
                return (res_ctx, res_value)

            # Step 4: Prepare for next iteration
            current_ctx = res_ctx
            current_node = next_node


    def on(self, res_value: Any, next_node: Optional[Self]) -> Self:
        self.value_to_next_node[res_value] = next_node
        return self
