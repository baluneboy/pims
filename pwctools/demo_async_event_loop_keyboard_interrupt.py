import asyncio
import logging
import time


async def do_work(i):
    print('start', i)

    # Work
    time.sleep(1)

    if i == 1:
        raise Exception('Bad')

    print('start asyncio', i)
    await asyncio.sleep(1)
    print('finished', i)
    return i


async def do_works():
    futures = [do_work(i) for i in range(2)]
    return await asyncio.gather(*futures)


async def do_works_with_catch_interrupt():
    try:
        return await do_works()
    except (asyncio.CancelledError, KeyboardInterrupt):
        print('Cancelled task')
    except Exception as ex:
        print('Exception:', ex)
    return None


def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    logging.basicConfig(level=logging.DEBUG)
    task = None
    try:
        task = asyncio.ensure_future(do_works_with_catch_interrupt())
        result = loop.run_until_complete(task)
        print('Result: {}'.format(result))
    except KeyboardInterrupt:
        if task:
            print('Interrupted, cancelling tasks')
            task.cancel()
            loop.run_forever()
            task.exception()
    finally:
        loop.close()


main()
