from fastapi import APIRouter
from mythme.model.config import MythtvConfig
from mythme.utils.config import config

router = APIRouter()


@router.get("/configs/{cfg}")
def get_config(cfg: str) -> MythtvConfig:
    if not cfg == "mythtv":
        raise ValueError(f"Unsupported config: {cfg}")
    return config.mythtv
