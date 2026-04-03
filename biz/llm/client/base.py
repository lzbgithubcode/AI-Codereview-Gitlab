from abc import abstractmethod
from typing import List, Dict, Optional

from biz.llm.types import NotGiven, NOT_GIVEN
from biz.utils.log import logger


class BaseClient:
    """ Base class for chat models client. """

    def ping(self) -> bool:
        """Ping the model to check connectivity."""
        try:
            # 简单的ping测试，发送一个简单的请求，只要不报错就认为连接正常
            result = self.completions(messages=[{"role": "user", "content": "你好"}])
            return result is not None and len(result.strip()) > 0
        except Exception as e:
            logger.error(f"尝试连接LLM失败: {e}")
            return False

    @abstractmethod
    def completions(self,
                    messages: List[Dict[str, str]],
                    model: Optional[str] | NotGiven = NOT_GIVEN,
                    ) -> str:
        """Chat with the model.
        """
