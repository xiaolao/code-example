from contextlib import ExitStack, AsyncExitStack
from contextlib import AbstractContextManager, AbstractAsyncContextManager


class AbcWorker:

    async def run(self):
        raise NotImplementedError

    async def __call__(self):
        mro_names = {cls.__name__ for cls in self.__class__.mro()}
        if "BaseMixIn" not in mro_names:
            return await self.run()
        async with AsyncExitStack() as async_stack:
            with ExitStack() as stack:
                for cls in self.__class__.__bases__:
                    if not getattr(cls, "context", None):
                        continue
                    context = getattr(cls, "context")
                    option = self.option.contexts.get(context.attr_name)
                    if issubclass(context, AbstractContextManager):
                        attr = stack.enter_context(context(option))
                        setattr(self, context.attr_name, attr)
                    elif issubclass(context, AbstractAsyncContextManager):
                        attr = await async_stack.enter_async_context(context(option))
                        setattr(self, context.attr_name, attr)
                return await self.run()
