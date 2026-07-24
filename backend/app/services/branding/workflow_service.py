import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.models.workflow import WorkflowProfile

logger = logging.getLogger("yt_splitter")

class WorkflowService:
    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[4]
        self.root_dir = root_dir
        self.config_path = self.root_dir / "assets" / "workflows" / "workflows.json"
        self.workflows: Dict[str, WorkflowProfile] = {}
        self._load_workflows()

    def _load_workflows(self):
        if not self.config_path.exists():
            logger.warning(f"Workflow config not found at {self.config_path}")
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for wf_id, cfg in data.items():
                profile = WorkflowProfile(
                    id=wf_id,
                    display_name=cfg.get("display_name", wf_id),
                    description=cfg.get("description", ""),
                    aspect_ratio=cfg.get("aspect_ratio", "original"),
                    padding_mode=cfg.get("padding_mode", "black_bars"),
                    allow_intro_outro=cfg.get("allow_intro_outro", True),
                    enable_subtitles=cfg.get("enable_subtitles", False),
                    subtitle_preset=cfg.get("subtitle_preset", "tiktok"),
                    enable_thumbnails=cfg.get("enable_thumbnails", True),
                    export_preset=cfg.get("export_preset", "high_quality")
                )
                self.workflows[wf_id] = profile

            logger.info(f"Loaded {len(self.workflows)} workflow profiles from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to parse workflow profiles: {e}", exc_info=True)

    def get_all_workflows(self) -> List[WorkflowProfile]:
        self._load_workflows()
        return list(self.workflows.values())

    def get_workflow(self, workflow_id: str) -> WorkflowProfile:
        self._load_workflows()
        wf = self.workflows.get(workflow_id)
        if not wf:
            raise KeyError(f"Workflow profile '{workflow_id}' does not exist.")
        return wf

workflow_service = WorkflowService()
