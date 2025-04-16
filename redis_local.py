from fastapi import FastAPI
from redis import Redis
from fastapi.responses import JSONResponse

import httpx
import json
import uvicorn
import asyncio


app = FastAPI()

async def query_from_database_fake():
    fake_data = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]

    await asyncio.sleep(5)
    return JSONResponse(content=fake_data)
    

@app.on_event("startup")
async def startup_event():
    app.state.redis = Redis(host='localhost', port=6379)


@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()


@app.get("/entries")
async def read_item():
    value = app.state.redis.get('entries') # Lấy entries từ Redis trước

    if value is not None: # Nếu có thì return luôn
        return value

    response = await query_from_database_fake() # Nếu không có thì lấy từ database
    value = response.body
    app.state.redis.set('entries', value, 50) # Lưu vào Redis
    return response
    
    
if __name__ == "__main__":
    uvicorn.run("redis_local:app", host="0.0.0.0", port=8000, reload=True)