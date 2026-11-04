import logging

#basicConfig 配全局日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",#时间 [级别] 消息
)

log = logging.getLogger("chief.api")