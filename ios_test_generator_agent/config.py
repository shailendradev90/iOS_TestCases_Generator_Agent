"""Configuration management for the iOS Test Generator Agent."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from .models import AgentConfig

DEFAULT_CONFIG_FILE = "ios-test-gen.yml"
ENV_PREFIX = "IOS_TEST_GEN_"


def load_config(
    config_path: str | Path | None = None,
    project_path: str | Path | None = None,
    **overrides: dict,
) -> AgentConfig:
    """Load configuration from file, environment, and overrides.

    Priority (highest to lowest):
    1. Explicit overrides (CLI arguments)
    2. Environment variables
    3. Config file
    4. Defaults
    """
    config_data: dict = {}

    # 1. Load from config file
    if config_path:
        config_path = Path(config_path)
    else:
        # Search for config file in project directory or CWD
        search_dirs = []
        if project_path:
            search_dirs.append(Path(project_path))
        search_dirs.append(Path.cwd())

        for search_dir in search_dirs:
            candidate = search_dir / DEFAULT_CONFIG_FILE
            if candidate.exists():
                config_path = candidate
                break

    if config_path and config_path.exists():
        with open(config_path) as f:
            file_data = yaml.safe_load(f) or {}
            config_data.update(file_data)

    # 2. Override with environment variables
    env_map = {
        f"{ENV_PREFIX}LLM_PROVIDER": "llm_provider",
        f"{ENV_PREFIX}MODEL": "model",
        f"{ENV_PREFIX}TEMPERATURE": "temperature",
        f"{ENV_PREFIX}MAX_TOKENS": "max_tokens",
        f"{ENV_PREFIX}PROJECT_PATH": "project_path",
        f"{ENV_PREFIX}OUTPUT_PATH": "output_path",
        f"{ENV_PREFIX}TEST_TARGET": "test_target_name",
        f"{ENV_PREFIX}TEST_FRAMEWORK": "test_framework",
        f"{ENV_PREFIX}GENERATE_MOCKS": "generate_mocks",
        f"{ENV_PREFIX}MOCK_FRAMEWORK": "mock_framework",
        "OPENAI_API_KEY": "_openai_api_key",
        "ANTHROPIC_API_KEY": "_anthropic_api_key",
        "GROQ_API_KEY": "_groq_api_key",
    }

    for env_var, config_key in env_map.items():
        value = os.environ.get(env_var)
        if value is not None:
            # Type coercion for known fields
            if config_key == "temperature":
                config_data[config_key] = float(value)
            elif config_key == "max_tokens":
                config_data[config_key] = int(value)
            elif config_key == "generate_mocks":
                config_data[config_key] = value.lower() in ("true", "1", "yes")
            else:
                config_data[config_key] = value

    # 3. Apply explicit overrides (filter out None values)
    clean_overrides = {k: v for k, v in overrides.items() if v is not None}
    config_data.update(clean_overrides)

    # Set project path if provided
    if project_path and "project_path" not in config_data:
        config_data["project_path"] = str(project_path)

    # Extract non-model fields
    config_data.pop("_openai_api_key", None)
    config_data.pop("_anthropic_api_key", None)

    # Build config object
    return AgentConfig(**{
        k: v for k, v in config_data.items()
        if k in AgentConfig.__dataclass_fields__
    })


def save_config(config: AgentConfig, path: str | Path) -> None:
    """Save configuration to a YAML file."""
    path = Path(path)
    data = {
        "llm_provider": config.llm_provider,
        "model": config.model,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "test_framework": config.test_framework,
        "include_setup_teardown": config.include_setup_teardown,
        "generate_mocks": config.generate_mocks,
        "mock_framework": config.mock_framework,
        "include_patterns": config.include_patterns,
        "exclude_patterns": config.exclude_patterns,
    }

    if config.test_target_name:
        data["test_target_name"] = config.test_target_name

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def generate_default_config(path: str | Path) -> Path:
    """Generate a default configuration file."""
    path = Path(path)
    config = AgentConfig()
    save_config(config, path)
    return path
