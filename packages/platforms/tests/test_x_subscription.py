# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""X subscription tier cache: one field, provenance, live outranks stored."""

from agoras.platforms.x.wrapper import X


def _x():
    return X(
        twitter_consumer_key='key',
        twitter_consumer_secret='secret',
        twitter_oauth_token='token',
        twitter_oauth_secret='token_secret',
    )


def test_tier_starts_unresolved():
    """A fresh wrapper has not resolved a tier yet."""
    x = _x()

    assert x._subscription_resolved is False
    assert x._subscription_type is None


def test_live_tier_outranks_a_stored_one():
    """A stale storage read must not downgrade a tier the API just reported."""
    x = _x()
    x._set_subscription('Basic', live=False)
    assert x._subscription_type == 'Basic'

    x._set_subscription('PremiumPlus', live=True)
    assert x._subscription_type == 'PremiumPlus'

    x._set_subscription(None, live=False)
    assert x._subscription_type == 'PremiumPlus'


def test_stored_reading_resolves_once():
    """A stored reading marks the tier resolved, including the free tier."""
    x = _x()
    x._set_subscription(None, live=False)

    assert x._subscription_resolved is True
    assert x._subscription_type is None
