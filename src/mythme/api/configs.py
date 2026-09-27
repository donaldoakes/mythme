from fastapi import APIRouter
from mythme.model.config import MythtvConfig
from typing import Optional
from mythme.utils.config import config
from mythme.utils.mythtv import get_storage_group_dirs as get_sg_dirs

router = APIRouter()


@router.get("/configs/{cfg}")
def get_config(cfg: str) -> MythtvConfig:
    if not cfg == "mythtv":
        raise ValueError(f"Unsupported config: {cfg}")
    return config.mythtv


@router.get("/configs/storage-group-dirs/{group_name}")
def get_storage_group_dirs(group_name: str) -> Optional[list[str]]:
    return get_sg_dirs(group_name)
