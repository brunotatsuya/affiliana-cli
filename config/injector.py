from typing import Optional
import inject


def setup_injector(injector_config: Optional[callable] = None):
    """
    This is a callable for configuring the "inject library" injector,
    which is used to magically inject dependencies.

    Args:
        injector_config (callable, optional): A function that receives a binder param
        and binds the instances of the dependencies to it. If not provided, it will
        be set to a lambda function that does nothing, just to have an (empty) injector set up.
    """
    if not injector_config:
        injector_config = lambda _: None
    inject.configure(injector_config)
