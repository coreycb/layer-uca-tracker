import os

from charmhelpers.core.hookenv import (
    config,
    open_port,
    status_set,
)

from charmhelpers.core.host import (
    chownr,
    service_restart,
)

import charmhelpers.core.host as ch_host

from charmhelpers.core.templating import render

from charmhelpers.fetch import (
    apt_install,
    install_remote,
)

from charms.layer import nginx

from charms.reactive import (
    remove_state,
    set_state,
    when,
    when_not,
)


def base_tracker_releases():
    if config('base-tracker-releases'):
        return config('base-tracker-releases').split()
    return None


def upstream_tracker_releases():
    if config('upstream-tracker-releases'):
        return config('upstream-tracker-releases').split()
    return None


template_map = {
    'generate-uca-reports': {
        'target': '/usr/local/bin/generate-uca-reports',
        'owner': 'root',
        'group': 'root',
        'perms': 0o755,
        'context': {
            'base_releases': base_tracker_releases(),
            'upstream_releases': upstream_tracker_releases(),
        },
    },
    'index.html': {
        'target': '/usr/share/nginx/www/index.html',
        'owner': 'www-data',
        'group': 'www-data',
        'perms': 0o644,
        'context': {
            'base_releases': base_tracker_releases(),
            'upstream_releases': upstream_tracker_releases(),
        },
    },
    'uca-tracker.service': {
        'target': '/etc/systemd/system/uca-tracker.service',
        'owner': 'root',
        'group': 'root',
        'perms': 0o644,
        'context': {},
    },
}


@when_not('uca-tracker.installed')
def install_uca_tracker():
    apt_install(['python3-git', 'python3-yaml', 'python3-httplib2',
                 'python3-launchpadlib'], fatal=True)

    install_remote('lp:ubuntu-reports', dest='/opt')

    for template, target_info in template_map.items():
        render(source=template,
               target=target_info['target'],
               owner=target_info['owner'],
               group=target_info['group'],
               perms=target_info['perms'],
               context=target_info['context'])

    if not os.path.exists('/var/log/uca-tracker'):
        os.mkdir('/var/log/uca-tracker')
    chownr('/usr/share/nginx/www', 'www-data', 'www-data')
    set_state('uca-tracker.installed')


@when('config.changed')
def update_config():
    remove_state('uca-tracker.installed')
    remove_state('uca-tracker.ready')


@when('nginx.available')
@when('uca-tracker.installed')
@when_not('uca-tracker.nginx.ready')
def setup_vhost():
    status_set('maintenance', 'setting up vhost')

    nginx.configure_site(
        'uca-tracker',
        'vhost.conf',
        app_path='/usr/share/nginx/www',
    )

    ch_host.service_restart('nginx')
    set_state('uca-tracker.nginx.ready')


@when('uca-tracker.nginx.ready')
@when_not('uca-tracker.ready')
def tracker_ready():
    open_port(80)

    service_restart('uca-tracker')
    status_set('active', 'ready')
    set_state('uca-tracker.ready')
