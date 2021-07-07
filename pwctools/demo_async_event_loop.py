import asyncio


async def get_inputs():
    while True:
        await asyncio.sleep(0.1)
        print("First Worker Executed")


async def set_outputs():
    while True:
        await asyncio.sleep(0.1)
        print("Second Worker Executed")


loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(get_inputs())
    asyncio.ensure_future(set_outputs())
    loop.run_forever()
except KeyboardInterrupt:
    print('Keyboard interrupt, so closing loop now.')
    pass
finally:
    print("Closing Loop")
    loop.close()
