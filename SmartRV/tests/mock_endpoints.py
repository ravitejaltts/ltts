import time

import uvicorn

from fastapi import FastAPI

from mock.connectivity import router as connectivity

app = FastAPI()
app.include_router(connectivity)


@app.get("/block_secs")
async def get_block_x_seconds(duration: int = 30):
    print(f'Sleeping {duration} seconds')
    time.sleep(duration)
    return {
        "message": f"Slept {duration} second"
    }


# Cradlepoint MOCK


if __name__ == '__main__':
    uvicorn.run(
        'mock_endpoints:app',
        host='0.0.0.0',
        port=int(8083),
        reload=1,
        # reload=1,
        log_level="error",
        workers=1,
        # limit_concurrency=5
    )
