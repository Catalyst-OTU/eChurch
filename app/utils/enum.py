import enum


class BaseEnum(enum.Enum):
    @classmethod
    def name_choices(cls):
        return tuple(i.name for i in cls)

    @classmethod
    def value_choices(cls):
        return tuple(i.value for i in cls)

    @classmethod
    def name_value_pair_choices(cls):
        return [(tag.name, tag.value) for tag in cls]
