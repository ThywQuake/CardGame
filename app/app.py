import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Optional
from pydantic import BaseModel
from typing import Literal

from app.core_bak.engine import Game

# --- Pydantic 模型：用于验证玩家输入 ---


class PlayerActionPayload(BaseModel):
    """
    定义玩家通过 WebSocket 发送的操作数据的结构。
    FastAPI 将自动验证这个结构。
    """

    type: Literal[
        "PLAY_CARD", "END_TURN", "CHOOSE_ITEM", "CHOOSE_POSITION", "SURRENDER", "OTHER"
    ]
    data: Dict = {}


# --- 游戏服务器类：管理 FastAPI 实例和游戏实例 ---


class GameServer:
    def __init__(self):
        # 实例化你的核心游戏逻辑
        self.game = Game()
        # 活跃的 WebSocket 连接字典: {player_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # 游戏循环参数
        self.fps = 10  # 游戏逻辑更新频率：每秒 10 次
        self.tick_interval = 1.0 / self.fps
        self.game_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, player_id: str):
        """处理新连接，并将其加入活跃连接列表。"""
        await websocket.accept()
        self.active_connections[player_id] = websocket
        print(f"Player {player_id} connected. Total: {len(self.active_connections)}")

    def disconnect(self, player_id: str):
        """处理断开连接。"""
        if player_id in self.active_connections:
            del self.active_connections[player_id]
            print(
                f"Player {player_id} disconnected. Total: {len(self.active_connections)}"
            )

    async def broadcast(self, message: Dict):
        """将消息广播给所有连接的客户端。"""
        # 注意：在实际项目中，您应该只发送给需要知道这个信息的玩家
        for player_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_json(message)
            except RuntimeError as e:
                # 处理连接断开的情况
                print(f"Error sending to {player_id}: {e}")
                self.disconnect(player_id)

    async def start_loop(self):
        """
        【系统通道】
        后台游戏循环的心跳驱动器。
        这个方法在应用启动时（on_event("startup")）被调用。
        """
        self.game.start_game()
        print("🟢 Game Loop Started via FastAPI startup event.")

        while True:
            # 1. 推动游戏逻辑更新和时间流逝
            self.game.tick(self.tick_interval)

            # 2. 从 EventManager 中获取新事件并广播
            # 假设 Game.event_manager 有一个 flush_events() 方法
            # 该方法返回自上次调用以来产生的所有事件
            # 并清空内部队列

            # 伪代码：
            # events = self.game.event_manager.flush_events()
            # if events:
            #     await self.broadcast({"type": "EVENTS", "data": events})

            # 3. 实时广播当前游戏阶段和倒计时（用于 UI 刷新）
            current_phase = self.game.phase.name

            # 假设可以从 action_manager 拿到当前 Action 的剩余时间
            # time_left = self.game.action_manager.get_time_left()

            await self.broadcast({
                "type": "STATUS_UPDATE",
                "phase": current_phase,
                # "time_left": time_left
            })

            # 4. 等待下一帧
            await asyncio.sleep(self.tick_interval)


# --- FastAPI 实例与路由 ---

app = FastAPI()
server = GameServer()


@app.on_event("startup")
async def startup_event():
    """应用启动时，将游戏循环放入后台任务。"""
    server.game_task = asyncio.create_task(server.start_loop())


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时，取消后台任务。"""
    if server.game_task:
        server.game_task.cancel()
        print("🔴 Game Loop Stopped.")


# --- WebSocket 路由：处理实时连接和玩家输入 ---


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    """
    【输入通道】
    处理玩家的 WebSocket 连接和操作。
    """
    await server.connect(websocket, player_id)

    # 理论上，您应该在这里验证 player_id 是否合法
    if player_id not in [server.game.zombie_player.id, server.game.plant_player.id]:
        # 可以拒绝连接或设置观察者模式
        pass

    try:
        while True:
            # 等待接收客户端发送的 JSON 数据
            data = await websocket.receive_json()

            try:
                # Pydantic 验证输入数据格式
                payload = PlayerActionPayload(**data)

                # 1. 将玩家操作数据传递给 Game 实例
                # Game.act_on() 会把数据交给 ActionManager 处理
                server.game.act_on(payload.dict())

                # 2. （可选）触发一次额外的 ActionManager.update()
                # 这样玩家的操作可以立即被处理，不等到下一个 tick
                # server.game.action_manager.update(dt=0.0)

            except Exception as e:
                # 数据验证失败或其他处理错误
                error_msg = f"Invalid payload or processing error: {e}"
                print(error_msg)
                await websocket.send_json({"error": error_msg, "original_data": data})

    except WebSocketDisconnect:
        # 连接断开时调用断开处理
        server.disconnect(player_id)
    except RuntimeError:
        # 客户端连接意外断开
        server.disconnect(player_id)
