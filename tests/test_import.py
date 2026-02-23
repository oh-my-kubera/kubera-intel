"""Smoke tests for package imports."""


def test_import_intel():
    import intel
    assert intel.__doc__


def test_import_subpackages():
    from intel.core import config
    from intel.core import credentials
    from intel.core import watchlist
    from intel.core.collectors import CollectedItem
    from intel.core.collectors import dart
    from intel.core.collectors import news
