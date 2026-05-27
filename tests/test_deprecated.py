"""Tests for deprecated decorator."""

import warnings
from wdecorators import deprecated


def test_deprecated_warns():
    @deprecated(version="1.0.0", alternative="new_func")
    def old():
        return "old result"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old()

        assert result == "old result"
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "old" in str(w[0].message)
        assert "new_func" in str(w[0].message)


def test_deprecated_version_only():
    @deprecated(version="2.0.0")
    def old():
        return "old"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old()
        assert result == "old"
        assert "since version 2.0.0" in str(w[0].message)


def test_deprecated_reason_only():
    @deprecated(reason="use the new API")
    def old():
        return "old"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old()
        assert result == "old"
        assert "use the new API" in str(w[0].message)


def test_deprecated_all_params():
    @deprecated(version="1.0.0", alternative="new_func", reason="better performance")
    def old():
        return "old"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old()
        assert result == "old"
        msg = str(w[0].message)
        assert "since version 1.0.0" in msg
        assert "use new_func instead" in msg
        assert "better performance" in msg


def test_deprecated_no_params():
    @deprecated()
    def old():
        return "old"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old()
        assert result == "old"
        assert "old is deprecated" == str(w[0].message)
