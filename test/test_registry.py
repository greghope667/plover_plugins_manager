import tarfile
import sys

import pkg_resources
import pytest

from plover_plugins_manager.registry import Registry
from plover_plugins_manager.plugin_metadata import PluginMetadata


@pytest.fixture
def fake_cache(tmpdir, monkeypatch):
    cache = tmpdir.join('cache.json')
    monkeypatch.setattr('plover_plugins_manager.global_registry.CACHE_FILE', str(cache))
    return cache

@pytest.fixture
def fake_index(monkeypatch):
    monkeypatch.setenv('PYPI_URL', 'test/data/index.json')

@pytest.fixture
def fake_working_set(tmpdir, monkeypatch):
    # Fake user site.
    tmp_user_site = tmpdir / 'user_site'
    tmp_user_site.mkdir()
    monkeypatch.setattr('site.USER_SITE', str(tmp_user_site))
    # Fake install prefix.
    tmp_prefix = tmpdir / 'prefix'
    tmp_prefix.mkdir()
    with tarfile.open('test/data/prefix.tar') as prefix:
        prefix.extractall(path=tmp_prefix)
    pr_state = pkg_resources.__getstate__()
    sys_path = sys.path[:]
    try:
        sys.path[:] = [str(tmp_prefix)]
        yield
    finally:
        sys.path[:] = sys_path
        pkg_resources.__setstate__(pr_state)

@pytest.fixture
def fake_env(fake_cache, fake_index, fake_working_set):
    pass


def test_bad_cache(fake_cache, fake_env):
    fake_cache.write('foobar')
    r = Registry()
    r.update()
    assert len(r) == 2

def test_readonly_cache(fake_cache, fake_env):
    fake_cache.write('{}')
    fake_cache.chmod(0o400)
    r = Registry()
    r.update()
    assert len(r) == 2

def test_registry(fake_cache, fake_env):
    r = Registry()
    r.update()
    assert len(r) == 2
    local_egg_info = r['local-egg-info']
    assert local_egg_info.current == PluginMetadata.from_kwargs(
        author='Local Egg-info',
        author_email='local.egg-info@mail.com',
        description='A macro plugin for Plover.',
        description_content_type='',
        home_page='http://localhost',
        keywords='',
        license='GNU General Public License v2 or later (GPLv2+)',
        name='local_egg_info',
        summary='Macro for Plover',
        version='2.0'
    )
    assert local_egg_info.available == []
    assert local_egg_info.latest is None
    assert local_egg_info.metadata is local_egg_info.current
    # Local only, .dist-info metadata, no metadata.json.
    local_dist_info = r['local-dist-info']
    assert local_dist_info.current == PluginMetadata.from_kwargs(
        author='Local Dist-info',
        author_email='local.dist-info@mail.com',
        description='A dictionary plugin for Plover.',
        description_content_type='',
        home_page='http://localhost',
        keywords='',
        license='GNU General Public License v2 or later (GPLv2+)',
        name='local_dist_info',
        summary='Macro for Plover',
        version='1.0.0'
    )
    assert local_dist_info.available == []
    assert local_dist_info.latest is None
    assert local_dist_info.metadata is local_dist_info.current
