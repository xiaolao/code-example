from contextlib import AbstractContextManager, AbstractAsyncContextManager


class BaseContext:
    """
    context meta class, check whether all subclass is context or async context.
    the attr_name will signed to workers.
    """

    attr_names = []

    def __init_subclass__(cls, attr_name: str=None, **kwargs):
        if not issubclass(cls, (AbstractContextManager, AbstractAsyncContextManager)):
            raise Exception(f"{cls.__name__} must be context")
        if issubclass(cls, AbstractContextManager) and issubclass(cls, AbstractAsyncContextManager):
            raise Exception(f"{cls.__name__} must be one of context or async context")
        if attr_name in cls.attr_names:
            raise Exception(f"{cls.__name__}: {attr_name} is already exists")
        cls.attr_name = attr_name
        cls.attr_names.append(attr_name)
        super().__init_subclass__(**kwargs)


class BaseMixIn:

    contexts = {}

    async_contexts = {}

    attributes = []

    def __init_subclass__(cls, context: BaseContext=None, **kwargs):
        if context is not None and issubclass(context, AbstractContextManager):
            cls.contexts.update({context.attr_name: context})
        elif context is not None and issubclass(context, AbstractAsyncContextManager):
            cls.async_contexts.update({context.attr_name: context})
        if cls.__bases__[0].__name__ == "BaseMixIn":
            for attr_name in cls.__dict__.keys():
                if attr_name.startswith("__"):
                    continue
                if attr_name in cls.attributes:
                    raise Exception(f"{cls.__name__}: {attr_name} is already exists")
                cls.attributes.append(attr_name)
        if context is not None:
            cls.context = context
        super().__init_subclass__(**kwargs)
