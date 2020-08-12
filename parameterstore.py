import os
import logging
class ParameterStore:
    def __init__(self, **kwargs):
        self.client = kwargs.get('session').client('ssm')
        self.path_delimiter = '/'

    @staticmethod
    def set_env(parameter_dict):
        for k, v in parameter_dict.items():
            os.environ.setdefault(k, v)

    def _get_paginated_parameters(self, client_method, strip_path=True, **get_kwargs):
        next_token = None
        parameters = []
        while True:
            result = client_method(**get_kwargs)
            parameters += result.get('Parameters')
            next_token = result.get('NextToken')
            if next_token is None:
                break
            get_kwargs.update({'NextToken': next_token})
        params_list=[]
        for p in parameters:
            params_list.append(self.extract_parameter(p, strip_path=strip_path))
        return params_list

    def extract_parameter(self, parameter, strip_path=True):
        key = parameter['Name']
        full_path = parameter['Name']
        if strip_path:
            key_parts = key.split(self.path_delimiter)
            sub_path = key_parts[3:] #Exclude prefix of path till environment.
            key = "/".join(sub_path) #include rest of the sub path as key
        value = parameter['Value']
        if parameter['Type'] == 'StringList':
            value = value.split(',')
        d={}
        d['key'] = key
        d['type'] = parameter['Type']
        d['value'] = parameter['Value']
        d['full_path'] = full_path
        return d

    def get_parameter(self, name, decrypt=True, strip_path=True):
        result = self.client.get_parameter(Name=name, WithDecryption=decrypt)
        p = result['Parameter']
        return dict([self.extract_parameter(p, strip_path=strip_path)])

    def get_parameters(self, names, decrypt=True, strip_path=True):
        get_kwargs = dict(Names=names, WithDecryption=decrypt)
        return self._get_paginated_parameters(
            client_method=self.client.get_parameters,
            strip_path=strip_path,
            **get_kwargs
        )

    def get_parameters_by_path(self, path, decrypt=True, recursive=True, strip_path=True):
        get_kwargs = dict(Path=path, WithDecryption=decrypt, Recursive=recursive)
        return self._get_paginated_parameters(
            client_method=self.client.get_parameters_by_path,
            strip_path=strip_path,
            **get_kwargs
        )

    def get_parameters_with_hierarchy(self, path, decrypt=True, strip_path=True):
        """Recursively get all parameters under path, keeping the hierarchy
        as a structure of nested dictionaries.
        """
        # Get a flat dictionary
        get_kwargs = dict(Path=path, WithDecryption=decrypt, Recursive=True)
        flat = self._get_paginated_parameters(
            client_method=self.client.get_parameters_by_path,
            strip_path=False,
            **get_kwargs
        )

        # Convert to a nested dictionary and strip leading path component
        result = {}

        for key, value in flat.items():
            if strip_path:
                key = key[len(path):]
            if key and key[0] == "/":
                key = key[1:]

            leafdict = result
            key_segments = key.split("/")
            for key_segment in key_segments[:-1]:
                leafdict = leafdict.setdefault(key_segment, {})
            leafdict[key_segments[-1]] = value

        return result
