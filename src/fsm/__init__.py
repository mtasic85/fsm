from .fsm import Node


def main() -> None:
    def a_run(ctx: dict) -> tuple[dict, str | None]:
        print('a_run', ctx)
        begin, end, current = ctx['begin'], ctx['end'], ctx['current']

        if begin <= current < end - 1:
            if current >= 5:
                # return ctx, 'end'
                # return ctx, 'error'
                raise Exception('a stop')

            ctx['current'] = current + 1
            return ctx, 'a'

        return ctx, 'end'

    def a_exc(ctx: dict, e: Exception) -> tuple[dict, str | None]:
        print('a_exc', ctx, e)
        return ctx, 'error'
        # return ctx, None

    def b_run(ctx: dict) -> tuple[dict, str | None]:
        print('b_run', ctx)
        return ctx, None
        # raise Exception('b stop')

    def b_exc(ctx: dict, e: Exception) -> tuple[dict, str | None]:
        print('b_exc', ctx, e)
        return ctx, 'error'

    a = Node(a_run, a_exc)
    b = Node(b_run, b_exc)

    a.on('a', a)
    a.on('end', None)
    a.on('error', b)

    b.on('error', None)

    ctx = {'begin': 0, 'end': 10, 'current': 0}
    a(ctx)
    print(ctx)
