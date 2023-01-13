import asyncio
from .server import run_coap, run_http

if __name__ == "__main__":
    print("Data proxy started")
    START_COMPUTE_R0 = None
    R0 = -1
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coap_task = loop.create_task(run_coap())
    http_task = loop.create_task(run_http())
    loop.run_until_complete(asyncio.gather(http_task, coap_task))
    
