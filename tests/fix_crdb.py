from typing import Optional

import pytest

from .utils import VersionCheck
from psycopg.crdb import CrdbConnection


def pytest_configure(config):
    # register libpq marker
    config.addinivalue_line(
        "markers",
        "crdb(version_expr, reason=detail): run/skip the test with matching CockroachDB"
        " (e.g. '>= 21.2.10', '< 22.1', 'skip < 22')",
    )


def check_crdb_version(got, mark):
    """
    Verify if the CockroachDB version is a version accepted.

    This function is called on the tests marked with something like::

        @pytest.mark.crdb("only")           # run on CRDB only, any version
        @pytest.mark.crdb                   # same as above
        @pytest.mark.crdb("only >= 21.1")   # run on CRDB only >= 21.1 (not on PG)
        @pytest.mark.crdb(">= 21.1")        # same as above
        @pytest.mark.crdb("skip")           # don't run on CRDB, any version
        @pytest.mark.crdb("skip < 22")      # don't run on CRDB < 22 (run on PG)

    and skips the test if the server version doesn't match what expected.
    """
    assert len(mark.args) <= 1
    assert not (set(mark.kwargs) - {"reason"})
    pred = VersionCheck.parse(mark.args[0] if mark.args else "only")
    pred.whose = "CockroachDB"

    msg = pred.get_skip_message(got)
    if not msg:
        return None

    reason = crdb_skip_message(mark.kwargs.get("reason"))
    if reason:
        msg = f"{msg}: {reason}"

    return msg


# Utility functions which can be imported in the test suite

is_crdb = CrdbConnection.is_crdb


def crdb_skip_message(reason: Optional[str]) -> str:
    msg = ""
    if reason:
        msg = reason
        if reason in _crdb_reasons:
            url = (
                "https://github.com/cockroachdb/cockroach/"
                f"issues/{_crdb_reasons[reason]}"
            )
            msg = f"{msg} ({url})"

    return msg


def skip_crdb(*args, reason=None):
    return pytest.param(*args, marks=pytest.mark.crdb("skip", reason=reason))


def crdb_encoding(*args):
    """Mark tests that fail on CockroachDB because of missing encodings"""
    return skip_crdb(*args, reason="encoding")


def crdb_time_precision(*args):
    """Mark tests that fail on CockroachDB because time doesn't support precision"""
    return skip_crdb(*args, reason="time precision")


def crdb_scs_off(*args):
    return skip_crdb(*args, reason="standard_conforming_strings=off")


# mapping from reason description to ticket number
_crdb_reasons = {
    "2-phase commit": 22329,
    "backend pid": 35897,
    "batch statements": 44803,
    "binary decimal": 82492,
    "cancel": 41335,
    "cast adds tz": 51692,
    "cidr": 18846,
    "composite": 27792,
    "copy canceled": 81559,
    "copy": 41608,
    "cursor with hold": 77101,
    "deferrable": 48307,
    "do": 17511,
    "encoding": 35882,
    "geometric types": 21286,
    "hstore": 41284,
    "infinity date": 41564,
    "interval style": 35807,
    "json array": 23468,
    "large objects": 243,
    "negative interval": 81577,
    "nested array": 32552,
    "notify": 41522,
    "password_encryption": 42519,
    "pg_terminate_backend": 35897,
    "range": 41282,
    "severity_nonlocalized": 81794,
    "scroll cursor": 77102,
    "server-side cursor": 41412,
    "stored procedure": 1751,
}
