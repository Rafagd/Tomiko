from collections.abc import MutableSet



class classproperty(object):
    def __init__(self, getter):
        self.getter = getter


    def __get__(self, instance, owner):
        return self.getter(owner)



class ttl_set(MutableSet):
    data = {}
    ttl  = 10


    def __init__(self, values = [], ttl=10):
        self.data = {}
        self.ttl  = ttl

        for value in values:
            self.add(value)


    def __contains__(self, item):
        return item.upper() in self.data


    def __len__(self):
        return len(self.data)


    def __iter__(self):
        for word in self.data:
            yield word


    def __repr__(self):
        return repr(self.data)


    def __str__(self):
        return ' '.join(self.data).strip()


    def add(self, item):
        self.data[item.upper()] = self.ttl


    def tick(self):
        new_data = {}

        for item in self.data:
            new_ttl = self.data[item] - 1

            if new_ttl >= 0:
                new_data[item] = new_ttl

        self.data = new_data


    def discard(self, item):
        del self.data[item.upper()]


