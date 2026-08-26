# -*- coding: utf-8 -*-

import pytest

from agoras.cli.registry import PlatformRegistry
from agoras.media.constraints import IMAGE, REGISTRY_MEDIA_PLATFORM_KEYS, VIDEO

_REGISTRY_ALIAS_TO_CANONICAL = {
    'x': 'twitter',
    'twitter': 'twitter',
}


def _canonical_registry_key(registry_key: str) -> str:
    return _REGISTRY_ALIAS_TO_CANONICAL.get(registry_key, registry_key)


@pytest.mark.parametrize('registry_key,platform_info', list(PlatformRegistry.PLATFORMS.items()))
def test_registry_media_platforms_have_contract_rows(registry_key, platform_info):
    """Every registry platform with post/video must map to IMAGE or VIDEO."""
    actions = platform_info.get('actions', set())
    if not actions & {'post', 'video'}:
        pytest.skip('no media actions')

    if registry_key == 'twitter':
        pytest.skip('duplicate registry entry for x/twitter')

    canonical = _canonical_registry_key(registry_key)
    assert canonical in IMAGE or canonical in VIDEO, (
        f'registry platform {registry_key!r} ({canonical}) missing IMAGE/VIDEO row'
    )


def test_registry_media_keys_match_contract_helper():
    """REGISTRY_MEDIA_PLATFORM_KEYS stays aligned with registry media platforms."""
    expected = set()
    for registry_key, platform_info in PlatformRegistry.PLATFORMS.items():
        if registry_key == 'twitter':
            continue
        if platform_info.get('actions', set()) & {'post', 'video'}:
            expected.add(_canonical_registry_key(registry_key))
    assert REGISTRY_MEDIA_PLATFORM_KEYS == frozenset(expected)
