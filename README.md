# 游戏架构规格说明书 (Game Architecture Specification)

## 1. 核心数据模型 (Data Models)

### 1.1 基础实体：卡牌 (Card)

所有卡牌必须包含的元数据：

| 属性 (Attribute) | 类型 (Type) | 说明 (Description)                                                        |
| ---------------- | ----------- | ------------------------------------------------------------------------- |
| `name`           | `string`    | 卡牌名称                                                                  |
| `description`    | `string`    | 效果描述                                                                  |
| `faction`        | `enum`      | 阵营：`ZOMBIE` / `PLANT`                                                  |
| `cost`           | `int`       | 消耗能量值                                                                |
| `rarity`         | `enum`      | `COMMON`, `UNCOMMON`, `RARE`, `SUPER_RARE`, `LEGENDARY`, `TOKEN`, `EVENT` |
| `class`          | `enum`      | 类型约束（见下文）                                                        |
| `pack`           | `enum`      | 扩展包：`BASIC`, `PREMIUM`, `GALACTIC`, `COLOSSAL`, `TRIASSIC`            |
| `tags`           | `string[]`  | 标签系统（体系联动核心）                                                  |
| `type`           | `enum`      | 核心分类：`FIGHTER`, `TRICK`, `ENVIRONMENT`                               |

**类型约束 (Class System):**

- **ZOMBIE:** `Beasty`, `Brainy`, `Crazy`, `Hearty`, `Sneaky`
- **PLANT:** `Guardian`, `Kabloom`, `Mega Grow`, `Smarty`, `Solar`

### 1.2 派生实体 (Derived Entities)

#### A. 单位 (Fighter)

- **继承:** 所有 `Card` 属性。
- **动态属性:**
- `strength` (int): 攻击力。
- `health` (int): 生命值（包含 `max_health` 与 `current_health`）。

- **能力 (Abilities):**
- **攻击型:** 必中 (`Bullseye`), 双重打击 (`Double Strike`), 穿透 (`Strikethrough`), 狂热 (`Frenzy`), 致命 (`Deadly`), 先攻 (`Overshoot`), 克制英雄 (`Anti-hero`), 溅射 (`Splashed Damage`)。
- **防御型:** 血攻 (`Health-attack`), 锦囊免疫 (`Untrickable`), 伤害免疫 (`Unhurtable`), 装甲 (`Armored`)。
- **特质型:** 组队 (`Team-up`), 两栖 (`Amphibious`), 狩猎 (`Hunt`), 墓碑 (`Tomb`)。

- **状态 (State):** `Hurt` (受伤), `Doom` (将死), `Frozen` (冻结)。

#### B. 英雄 (Hero)

- **血量 (Health):** 初始值 20。
- **超级格挡 (SuperBlock):**
- `energy_slot`: 8 格能量槽。
- `durability`: 3 点耐久度。
- `trigger`: 受到非必中伤害时，随机增加 1-3 格能量。

- **超能力 (Superpower):** 4 张专属 1c 卡牌。

---

## 2. 空间逻辑：场地 (Field Map)

游戏包含 5 条横向排列的路 (Lane)：

| 索引 (Index) | 类型 (Type)  | 环境位 (Env Slot) | 放置规则                         |
| ------------ | ------------ | ----------------- | -------------------------------- |
| Lane 1       | 高地 (High)  | 禁用              | 无法放置环境牌                   |
| Lane 2-4     | 平地 (Lawn)  | 启用              | 可放置环境牌，遵循“后发覆盖”原则 |
| Lane 5       | 水池 (Water) | 禁用              | 仅限具 `Amphibious` 能力单位放置 |

**单位容量约束 (Capacity):**

- **ZOMBIE:** 每路上限 1 个。
- **PLANT:** 每路上限 2 个（必须包含 1 个具 `Team-up` 能力的单位）。

---

## 3. 游戏流状态机 (Game Loop FSM)

### 3.1 单回合序列 (Turn Sequence)

1. **Turn Start:** 能量恢复，双方从 `Deck` 抽取一张 `Card`。
2. **Zombie Phase:** 仅限僵尸玩家操作，仅能打出 `Fighter` 卡牌。
3. **Plant Phase:** 仅限植物玩家操作，可打出任意类型卡牌。
4. **Zombie Trick Phase:** 仅限僵尸玩家操作，仅能打出 `Trick` 或 `Environment`。
5. **Combat Phase:** 自动结算。从 Lane 1 至 Lane 5 依次执行攻击。
6. **Turn End:** 双方剩余能量清零。

### 3.2 惊喜阶段中断 (Surprise Phase Interrupt)

当 `SuperBlock` 能量槽满且 `durability > 0` 时强制触发：

- **挂起 (Suspend):** 当前所有阶段逻辑中止。
- **免疫 (Immunity):** 该英雄进入无敌状态直至本阶段结束。
- **操作 (Action):** `energy_slot` 清零 -> `durability` 减一 -> 抽取并选择是否执行 `Superpower`（执行则不消能，保留则入手）。
- **恢复 (Resume):** 退出中断，返回原阶段。

---

## 4. 系统架构 (System Architecture)

### 4.1 事件驱动系统 (Event-Listener System)

- **Event:** 最小不可分割动作（例如：`DAMAGE_TAKEN`, `UNIT_DEATH`, `CARD_DRAWN`）。
- **Event Manager:** 处理事件优先级与队列排队。
- **Listener:** 监听特定事件并触发逻辑回复（例如：当 `Unit_A` 死亡时，`Unit_B` 攻击力 +1）。

### 4.2 操作栈管理器 (Action Stack Manager)

- **机制:** 采用栈 (Stack) 结构管理阻塞性操作。
- **Wait:** 后端开启计时器等待 Web 端输入。
- **Nested Action:** 支持在等待过程中由被动技能触发新的操作请求。

### 4.3 存储与通信 (Storage & Communication)

- **Static Storage:** 所有的卡牌、英雄、技能库必须以 `JSON` 格式静态化，确保逻辑与数据分离。
- **Replay System:** 记录所有对局操作 `JSON` 流，配合固定随机种子 (Seed) 实现 100% 回放。
- **Interface:** 前端使用 Canvas (推荐 Phaser/Pixi.js) 渲染；后端使用 Python 负责事件解析与状态合法性校验。
