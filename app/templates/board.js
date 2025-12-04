document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    const seats = document.querySelectorAll('.seat');

    // 存储座位占用状态的 Map
    const seatOccupancy = new Map();
    seats.forEach(seat => {
        // 初始化，每个座位的 ID 可以是它的 class 或 data 属性
        seatOccupancy.set(seat.id || seat.classList[1], null); // 值为 null 表示未占用
    });

    cards.forEach(card => {
        let isDragging = false;
        let startX, startY;

        // 确保卡牌有唯一的 ID，方便后续状态追踪
        if (!card.dataset.cardId) {
            // 实际项目中应使用更严谨的 ID
            card.dataset.cardId = Math.random().toString(36).substring(7);
        }

        // 监听器注册 (保持不变)
        card.addEventListener('mousedown', dragStart);
        card.addEventListener('touchstart', dragStart, { passive: true });

        function dragStart(e) {
            // ... dragStart 逻辑保持不变 ...
            isDragging = true;
            if (e.type === 'mousedown' && e.button !== 0) return;
            e.preventDefault();

            const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            const clientY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;

            startX = clientX;
            startY = clientY;

            card.style.transition = 'none';

            document.addEventListener('mousemove', dragMove);
            document.addEventListener('mouseup', dragEnd);
            document.addEventListener('touchmove', dragMove);
            document.addEventListener('touchend', dragEnd);
        }

        function dragMove(e) {
            // ... dragMove 逻辑保持不变 ...
            if (!isDragging) return;

            const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            const clientY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;

            const deltaX = clientX - startX;
            const deltaY = clientY - startY;

            card.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
        }

        // 核心修正：添加投放检测和状态判断
        function dragEnd(e) {
            if (!isDragging) return;
            isDragging = false;

            document.removeEventListener('mousemove', dragMove);
            document.removeEventListener('mouseup', dragEnd);
            document.removeEventListener('touchmove', dragMove);
            document.removeEventListener('touchend', dragEnd);

            let targetSeat = null;
            const cardRect = card.getBoundingClientRect();

            seats.forEach(seat => {
                // 检查座位是否已占用
                const seatKey = seat.id || seat.classList[1];
                if (seatOccupancy.get(seatKey) !== null) {
                    return; // 💥 已占用，跳过此座位
                }

                const seatRect = seat.getBoundingClientRect();

                const isColliding = (
                    cardRect.left < seatRect.right &&
                    cardRect.right > seatRect.left &&
                    cardRect.top < seatRect.bottom &&
                    cardRect.bottom > seatRect.top
                );

                if (isColliding) {
                    targetSeat = seat;
                }
            });

            if (targetSeat) {
                // 命中未占用的投放区：打出卡牌
                playCardToSeat(card, targetSeat);

            } else {
                // 未命中或座位已占用：执行松手弹回逻辑
                snapBack(card);
            }
        }
    });

    // 弹回原位的通用函数
    function snapBack(card) {
        card.style.transition = 'transform 0.3s ease-out';
        card.style.transform = 'translate(0px, 0px)';
    }

    /**
     * 模拟向后端 POST 打出卡牌信息
     */
    async function postCardPlay(cardId, seatId) {
        const endpoint = 'YOUR_BACKEND_API_ENDPOINT/play_card'; // 替换为你的真实 API 地址

        try {
            // 模拟网络延迟
            await new Promise(resolve => setTimeout(resolve, 300));

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    card_id: cardId,
                    seat_id: seatId,
                    // 可添加其他游戏数据，如玩家 ID 等
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Backend response:', result);

            // 成功：返回 true
            return true;

        } catch (error) {
            console.error('Error posting card play:', error);
            alert('打出卡牌失败，请重试！');
            // 失败：返回 false
            return false;
        }
    }


    /**
     * 打出卡牌的主逻辑
     */
    async function playCardToSeat(card, seat) {
        const cardId = card.dataset.cardId;
        const seatId = seat.id || seat.classList[1];

        // 1. **视觉反馈：卡牌移动到座位中心** (卡牌形状不变)
        // 获取座位中心相对于卡牌父容器的位置，并计算偏移量
        const seatRect = seat.getBoundingClientRect();
        const cardParentRect = card.parentNode.getBoundingClientRect();

        // 计算卡牌移动到座位中心所需的 translate 距离
        const targetX = (seatRect.left + seatRect.right) / 2 - (cardRect.left + cardRect.right) / 2;
        const targetY = (seatRect.top + seatRect.bottom) / 2 - (cardRect.top + cardRect.bottom) / 2;

        card.style.transition = 'transform 0.2s ease-in';
        card.style.transform = `translate(${targetX}px, ${targetY}px)`;

        // 2. **发送后端请求**
        const success = await postCardPlay(cardId, seatId);

        if (success) {
            // 3. **成功：更新游戏状态**

            // 标记座位已占用，并存储打出的卡牌 ID
            seatOccupancy.set(seatId, cardId);
            seat.classList.add('occupied');

            // 移除卡牌的拖拽能力 (表示卡牌已打出)
            card.removeEventListener('mousedown', dragStart);

            // 视觉：卡牌变灰或消失 (取决于游戏设计)
            card.style.opacity = '0.5';
            card.style.pointerEvents = 'none';

            console.log(`Card ${cardId} successfully played to seat ${seatId}.`);

        } else {
            // 4. **失败：卡牌弹回**
            snapBack(card);
        }
    }
});