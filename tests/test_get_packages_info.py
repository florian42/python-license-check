import sys

import pytest

from liccheck.command_line import get_packages_info


def test_license_strip(tmpfile):
    tmpfh, tmppath = tmpfile
    tmpfh.write("pip\n")
    tmpfh.close()
    assert get_packages_info(tmppath)[0]["licenses"] == ["MIT"]


def test_requirements_markers(tmpfile):
    tmpfh, tmppath = tmpfile
    tmpfh.write(
        "python-openid;python_version<=\"2.7\"\n"
        "python3-openid;python_version>=\"3.0\"\n"
    )
    tmpfh.close()
    if sys.version_info.major == 3:
        assert len(get_packages_info(tmppath)) == 2
    else:
        assert len(get_packages_info(tmppath)) == 1


def test_editable_requirements_get_ignored(tmpfile):
    tmpfh, tmppath = tmpfile
    tmpfh.write(
        "-e file:some_editable_req\n"
        "pip\n"
    )
    tmpfh.close()

    packages_info = get_packages_info(tmppath)
    assert len(packages_info) == 1
    assert packages_info[0]["name"] == "pip"


@pytest.mark.parametrize(
    ('no_deps', 'expected_packages'), (
        pytest.param(
            False,
            ('configparser', 'liccheck', 'semantic-version', 'toml'),
            marks=pytest.mark.skipif(
                sys.version_info[0] < 3,
                reason='with py2 there are more dependencies',
            ),
            id='with deps'
        ),
        pytest.param(True, ('liccheck',), id='without deps'),
    )
)
def test_deps(tmpfile, no_deps, expected_packages):
    tmpfh, tmppath = tmpfile
    tmpfh.write('liccheck\n')
    tmpfh.close()
    packages_info = get_packages_info(tmppath, no_deps)
    packages = tuple(package['name'] for package in packages_info)
    assert packages == expected_packages

@pytest.mark.parametrize(
    ('mode', 'expected_license'), (
            pytest.param('mixed', (['BSD'], ['MIT']), id='mixed'),
            pytest.param('classifier', (['BSD'], ['MIT']), id='classifier'),
            pytest.param('metadata', (['BSD (3 clause)'],  ['MIT']), id='metadata'),
    )
)
def test_mode(tmpfile, mode, expected_license):
    tmpfh, tmppath = tmpfile
    tmpfh.write('prettytable\n')
    tmpfh.close()
    packages_info = get_packages_info(tmppath, mode=mode)
    packages = tuple(package['licenses'] for package in packages_info)
    assert packages == expected_license
