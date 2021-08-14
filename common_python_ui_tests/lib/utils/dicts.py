import re


class DotDict(dict):
    """Dict that expose it's keys as attributes"""

    def getattr(self, key):
        if key in self:
            return self[key]
        raise AttributeError

    def init(self, d):
        self.update(**dict((k, self.parse(v))
                           for k, v in d.items()))

    @classmethod
    def parse(cls, v):
        if isinstance(v, dict):
            return cls(v)
        elif isinstance(v, list):
            return [cls.parse(i) for i in v]
        else:
            return v

    def dir(self):
        dict_attrs = ["clear", "has_key", "itervalues", "popitem", "viewitems", "copy", "items", "keys", "setdefault",
                      "viewkeys", "fromkeys", "iteritems", "parse", "update", "viewvalues", "get", "iterkeys", "pop",
                      "values"]

        return dict_attrs + self.keys()


class FlatDict(dict):
    def init(self, *args, **kwargs):
        self.dict = kwargs
        if args and (isinstance(args[0], dict) or isinstance(args[0], list)):
            dict.init(self, self.from_flat(args[0]))
        else:
            dict.init(self, *args, **kwargs)

    def getitem(self, key):
        current = self
        for k in self.flat_key(key):
            cls = list if isinstance(current, list) else dict
            current = cls.getitem(current, k)

        return current

    def setitem(self, key, value):
        self.update(self.from_flat({key: value}))

    def delitem(self, key):
        flat_key = self.flat_key(key)
        del_key = flat_key.pop()

        if flat_key:
            target = self[self.str_key(flat_key)]
            del (target[del_key])
        else:
            dict.delitem(self, del_key)

    def contains(self, item):
        try:
            self[item]
        except KeyError:
            return False
        else:
            return True

    def flatten(self):
        def is_enumerable(node):
            return isinstance(node, list) or isinstance(node, dict)

        def enum(node):
            if isinstance(node, list):
                return enumerate(node)
            elif isinstance(node, dict):
                return list(node.items())
            else:
                raise Exception('Cannot create enum for node that is not a list {0}'.format(node))

        def path_str(path):
            return '.'.join(map(str, path))

        def walk(node, path):
            for key, value in enum(node):
                path.append(key)
                if is_enumerable(value):
                    walk(value, path)
                else:
                    result[path_str(path)] = value
                path.pop()

        result = {}
        walk(self, [])

        return result

    def flatmerge(self, dic):
        self_flatten = self.flatten()
        other_flatten = self.flat(dic).flatten()
        self_flatten.update(other_flatten)

        return FlatDict(self_flatten)

    def flatupdate(self, dic):
        other_flatten = self.flat(dic).flatten()

        for k, v in list(other_flatten.items()):
            self[k] = v

    @classmethod
    def from_flat(cls, dic):
        def unfold_key(path, keys, value):
            current_key = keys.pop(0)
            if len(keys) == 0:
                set_key(path, current_key, value)
                return
            next_key = keys[0]
            if not has_key(path, current_key):
                init_key(path, current_key, next_key)

            return unfold_key(path[current_key], keys, value)

        def init_key(path, current_key, next_key):
            value = [] if isinstance(next_key, int) else {}
            set_key(path, current_key, value)

        def has_key(path, key):
            if isinstance(key, int):
                return len(path) > key and path[key] is not None
            return key in path

        def set_key(path, key, value):
            if isinstance(key, int):
                while len(path) <= key:
                    path.append(None)
            path[key] = value

        if isinstance(dic, list):
            dic = cls.list_to_dict(dic)

        unfolded = {}
        for key, value in list(dic.items()):
            if cls.is_str(key):
                unfold_key(unfolded, cls.flat_key(key), value)
            else:
                unfolded[key] = value

        return unfolded

    @classmethod
    def flat_key(cls, key):
        flat = re.sub(r'\]', '', re.sub(r'\[', '.', str(key)))
        return [int(x) if x.isdigit() else x for x in flat.split('.')]

    @classmethod
    def str_key(cls, key):
        return '.'.join(map(str, key))

    @classmethod
    def flat(cls, obj):
        if isinstance(obj, FlatDict):
            return obj
        if isinstance(obj, list):
            return cls(cls.list_to_dict(obj))
        if isinstance(obj, dict):
            return cls(obj)

        raise TypeError('Cannot flatten anything except list, dict or FlatDict')

    @staticmethod
    def list_to_dict(lst):
        return {k: v for k, v in enumerate(lst)}

    @staticmethod
    def is_str(key):
        return isinstance(key, str)
