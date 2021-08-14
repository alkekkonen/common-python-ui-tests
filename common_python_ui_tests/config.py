# -*- coding: UTF-8 -*-

import os
import sys
import yaml
import logging
import requests
# from hyperclient.utils.data import DotDict
from io import StringIO

CONSUL_URL_PATTERN = 'https://consul-url/{env}/tests/config?raw&token={token}'
DEFAULT_TOKEN = 'deadbeef-1337-a110-0101-012345678910'

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
FOLDER = os.path.join(PATH, 'config')


def initialize_config(env: str, **kwargs: dict) -> object:
    env_file_mask = f'{FOLDER}/{env}'
    env_file = f"{env_file_mask}.env"
    if os.path.exists(env_file):
        log.info('Loading config in env format')
        return EnvConfig(env, **kwargs).config
    yaml_file = f"{env_file_mask}.yml"
    if os.path.exists(yaml_file):
        log.info('Loading config in yml format')
        return YmlConfig(env)
    raise ValueError(f'Could not find configuration for {env}')


class EnvConfig:
    def __init__(self, env, use_consul=None, jwt=None):
        self.env = env
        self.use_consul = use_consul
        self.jwt = jwt
        self.config = self._load()

    def _load(self):
        if self.use_consul:
            log.info('Loading config from Consul')
            token = self.jwt or self.__get_token()
            log.info('Using token {}.'.format(token))
            url = CONSUL_URL_PATTERN.format(env=self.env, token=token)
            request = requests.get(url)
            if request.status_code == 200:
                log.info('Loading config files from url {}'.format(url))
                result = yaml.load(request.text)
            else:
                raise Exception('Could not download configuration from {}'.format(url))
        else:
            log.info('Loading config from env file')
            env_config = '{}.env'.format(self.env)
            default_config = '{}.env'.format('default')
            config_dir = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'config')
            if env_config not in os.listdir(config_dir):
                log.exception('Env file with name [{0}] not found in config directory'.format(env_config))
                raise ValueError('environment {0} cannot be found in config directory'.format(env_config))

            env_config_path = os.path.join(config_dir, env_config)
            default_config_path = os.path.join(config_dir, default_config)

            result = {}

            # add to result data from default config
            if os.path.exists(default_config_path):
                result.update(read_config(default_config_path))

            # update values in result with data from current env config
            result.update(read_config(env_config_path))

        if '--browser' in sys.argv:
            result['default_browser'] = sys.argv[sys.argv.index('--browser') + 1]

        if '--screenshots' in sys.argv:
            result['screenshots'] = sys.argv[sys.argv.index('--screenshots') + 1]
            assert os.path.isdir(result['screenshots'])

        return DotDict(result)

    def __get_token(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'config', 'jwt_per_env.yml')
        log.info('Trying to get token from {}'.format(path))
        return read_yaml(path).get(self.env, )


def read_yaml(path):
    with open(path) as f:
        data = f.read()
    return yaml.load(data)


def read_config(path):
    return read_yaml(path)


def prepare_file_to_yaml(file_path, files_read=None, to_return="Stream"):
    files_read = files_read or []
    folder, name = os.path.split(os.path.abspath(file_path))
    files = os.listdir(folder)
    lines = []
    with open(file_path) as file_descriptor:
        for line in file_descriptor.readlines():
            if line.startswith("!include"):
                names_to_include = line.split()[1:]
                for name_to_include in names_to_include:
                    if name_to_include not in files:
                        raise FileNotFoundError(f"Nothing to include. There is no file {name_to_include} in {folder}.")
                    if name_to_include in files_read:
                        raise ValueError(
                            f"Cyclic dependencies after chain {files_read} there is a file {name_to_include} again")
                    lines_to_include = prepare_file_to_yaml(os.path.join(folder, name_to_include),
                                                            files_read=files_read + [name],
                                                            to_return="Lines")
                    for line_of_dependency in lines_to_include:
                        lines.append(line_of_dependency)
                    lines.append("\n")
                    lines.append("\n")
            else:
                lines.append(line)
    if to_return == "Lines":
        return lines
    if to_return == "Stream":
        return StringIO("".join(lines))
    if to_return == "String":
        return "".join(lines)
    raise ValueError(f"I don't know how to return {to_return}")


class YmlConfig:
    def __init__(self, env: str):
        self.update(env)

    def update(self, env):
        self._load_from_disk(env)

    def _load_from_disk(self, env):
        log.info(f'Loading config files from dir [{FOLDER}]')
        stream = prepare_file_to_yaml(os.path.join(FOLDER, f"{env}.yml"))
        data_dict = yaml.load(stream)
        result = data_dict['default']
        if env != 'default':
            result.update(data_dict[env])
        if '--browser' in sys.argv:
            result['default_browser'] = sys.argv[sys.argv.index('--browser') + 1]

        if '--screenshots' in sys.argv:
            result['screenshots'] = sys.argv[sys.argv.index('--screenshots') + 1]
            assert os.path.isdir(result['screenshots'])
        self._data = DotDict(result)

    def __getattr__(self, item: str):
        return self._data[item]

    def __getitem__(self, item):
        return self.__getattr__(item)

    def get(self, item, default=None):
        try:
            return self.__getattr__(item)
        except KeyError:
            if default is not None:
                return default
            raise

    def __contains__(self, value):
        return value in self._data
