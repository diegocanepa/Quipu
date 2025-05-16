import logging
from enum import Enum

from config import config

logger = logging.getLogger(__name__)


class FeatureFlag:
    """
    Class to manage feature flags.
    """

    def __init__(self, is_enabled: bool, disabled_message: str):
        self.is_enabled = is_enabled
        self.disabled_message = disabled_message


class FeatureFlagsEnum(Enum):
    AUDIO_TRANSCRIPTION = 1
    TRANSFER = 2
    EXCHANGE = 3
    TRANSACTION = 4
    INVESTMENT = 5


FEATURE_FLAGS = {
    FeatureFlagsEnum.AUDIO_TRANSCRIPTION: FeatureFlag(
        is_enabled=config.FF_AUDIO_TRANSCRIPTION,
        disabled_message="La transcripción de audio está deshabilitada 🙁 \n\n 🚀 Proximamente se podrá usar  ",
    ),
    FeatureFlagsEnum.TRANSFER: FeatureFlag(
        is_enabled=config.FF_TRANSFER,
        disabled_message="Las transferencias están deshabilitadas 🙁 \n\n 🚀 Proximamente se podrá usar",
    ),
    FeatureFlagsEnum.EXCHANGE: FeatureFlag(
        is_enabled=config.FF_EXCHANGE,
        disabled_message="Los intercambios están deshabilitados 🙁 \n\n 🚀 Proximamente se podrá usar",
    ),
    FeatureFlagsEnum.TRANSACTION: FeatureFlag(
        is_enabled=config.FF_TRANSACTION,
        disabled_message="Las transacciones están deshabilitadas 🙁 \n\n 🚀 Proximamente se podrá usar",
    ),
    FeatureFlagsEnum.INVESTMENT: FeatureFlag(
        is_enabled=config.FF_INVESTMENT,
        disabled_message="Las inversiones están deshabilitadas 🙁 \n\n 🚀 Proximamente se podrá usar",
    ),
}


def is_feature_enabled(feature: FeatureFlagsEnum) -> bool:
    """
    Check if a feature is enabled.

    Args:
        feature (FeatureFlagsEnum): The feature to check.

    Returns:
        bool: True if the feature is enabled, False otherwise.
    """
    if not FEATURE_FLAGS[feature].is_enabled:
        logger.log(
            logging.WARNING,
            f"Feature '{feature.name}' is disabled.",
        )

    return FEATURE_FLAGS[feature].is_enabled


def get_disabled_message(feature: FeatureFlagsEnum) -> str:
    """
    Get the disabled message for a feature.

    Args:
        feature (FeatureFlagsEnum): The feature to check.

    Returns:
        str: The disabled message.
    """
    return FEATURE_FLAGS[feature].disabled_message
