"""商品发布校验策略（见设计说明书 4.5 策略模式）。

后续实现：出售必须填写价格；求购/交换价格可为空；交换可校验换入类型等。
"""

from abc import ABC, abstractmethod

from fastapi import HTTPException, status

from app.schemas.item import ItemCreate


class PublishStrategy(ABC):
    @abstractmethod
    def validate(self, payload: ItemCreate) -> None:
        """校验失败时抛出 fastapi.HTTPException(400)。"""


class SaleStrategy(PublishStrategy):
    def validate(self, payload: ItemCreate) -> None:
        if payload.price is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="出售商品必须填写价格",
            )


class WantBuyStrategy(PublishStrategy):
    def validate(self, payload: ItemCreate) -> None:
        return None


class ExchangeStrategy(PublishStrategy):
    def validate(self, payload: ItemCreate) -> None:
        return None


_STRATEGIES: dict[int, PublishStrategy] = {
    1: SaleStrategy(),
    2: WantBuyStrategy(),
    3: ExchangeStrategy(),
}


def get_publish_strategy(item_type: int) -> PublishStrategy:
    try:
        return _STRATEGIES[item_type]
    except KeyError as exc:
        raise ValueError(f"未知的商品类型: {item_type}") from exc
