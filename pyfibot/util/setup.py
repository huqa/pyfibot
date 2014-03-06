# -*- coding: utf-8 -*-
from __future__ import print_function, division
import yaml
import os
import shlex
import subprocess


def get_network():
    print()
    print('Adding network')
    print('--------------')
    alias = raw_input('Network alias [empty to stop]: ').strip()
    if not alias:
        return None, None

    network = {}
    network['server'] = raw_input('Server: ').strip()
    network['channels'] = raw_input('Channels [separated by space]: ').strip().split()
    password = raw_input('Server password [empty if none]: ').strip()
    if password:
        network['password'] = password

    return alias, network


def generate_config():
    print()
    print('Generate initial configuration')
    print('------------------------------')
    config = {}
    config['nick'] = raw_input('Bot nickname: ').strip()
    config['admins'] = raw_input('Admin hostmasks [separated by space]: ').strip().split()
    config['networks'] = {}
    while True:
        alias, network = get_network()
        if not alias:
            break

        config['networks'][alias] = network

    return config


def install_requirements(botdir):
    print()
    print('Installing required packages')
    print('----------------------------')
    with open(os.path.join(botdir, '.travis.yml'), 'r') as f:
        travis_conf = yaml.load(f.read())
    for c in travis_conf['install']:
        # Hack for setuptools version.. Will be removed, once 3.0 is fully supported
        c = c.replace('$SETUP_TOOLS', '<3.0')
        cmd = shlex.split(c)
        cmd[0] = os.path.join(os.path.join(botdir, 'bin'), cmd[0])
        # print(cmd)
        subprocess.call(cmd)
    print()
    print('Packages installed')


if __name__ == '__main__':
    import sys
    botdir = sys.argv[1]
    install_requirements(botdir)
    config_file = os.path.join(botdir, 'config.yml')

    print()
    if os.path.exists(config_file):
        print('Configuration file exists, skipping creation.')
    else:
        config = generate_config()
        print()
        print('Saving configuration to "config.yml".')
        with open(config_file, 'w') as f:
            f.write(yaml.dump(config, encoding='utf-8', default_flow_style=False))

    print()
    print()
    print('Installation finished, use "./run.sh" to start the bot!')
