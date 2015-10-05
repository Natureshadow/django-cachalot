# coding: utf-8

from __future__ import unicode_literals
from collections import defaultdict

from django.conf import settings
from django.db import connections
from django.utils.six import string_types

from .cache import cachalot_caches
from .utils import _get_table_cache_key, _invalidate_table_cache_keys


__all__ = ('invalidate',)


def _get_table_cache_keys_per_cache(tables, cache_alias, db_alias):
    no_tables = not tables
    cache_aliases = settings.CACHES if cache_alias is None else (cache_alias,)
    db_aliases = settings.DATABASES if db_alias is None else (db_alias,)
    table_cache_keys_per_cache = defaultdict(list)
    for db_alias in db_aliases:
        if no_tables:
            tables = connections[db_alias].introspection.table_names()
        for cache_alias in cache_aliases:
            table_cache_keys = [
                _get_table_cache_key(db_alias, t) for t in tables]
            if table_cache_keys:
                table_cache_keys_per_cache[cache_alias].extend(table_cache_keys)
    return table_cache_keys_per_cache


def _get_tables(tables_or_models):
    return [o if isinstance(o, string_types) else o._meta.db_table
            for o in tables_or_models]


def invalidate(tables_or_models=(), cache_alias=None, db_alias=None):
    """
    Clears what was cached by django-cachalot implying one or more SQL tables
    or models from ``tables_or_models``.  If ``tables_or_models``
    is not specified, all tables found in the database are invalidated.

    If ``cache_alias`` is specified, it only clears the SQL queries stored
    on this cache, otherwise queries from all caches are cleared.

    If ``db_alias`` is specified, it only clears the SQL queries executed
    on this database, otherwise queries from all databases are cleared.

    :arg tables_or_models: SQL tables names
    :type tables_or_models: iterable of strings or models, or NoneType
    :arg cache_alias: Alias from the Django ``CACHES`` setting
    :type cache_alias: string or NoneType
    :arg db_alias: Alias from the Django ``DATABASES`` setting
    :type db_alias: string or NoneType
    :returns: Nothing
    :rtype: NoneType
    """

    table_cache_keys_per_cache = _get_table_cache_keys_per_cache(
        _get_tables(tables_or_models), cache_alias, db_alias)
    for cache_alias, table_cache_keys in table_cache_keys_per_cache.items():
        _invalidate_table_cache_keys(cachalot_caches.get_cache(cache_alias),
                                     table_cache_keys)
