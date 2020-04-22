import logging

log = logging.getLogger(__name__)


class ServiceProvider:
    SERVICE_NAME = None
    SERVICE_DOMAIN = None

    def __init__(self):
        assert all([self.SERVICE_NAME, self.SERVICE_DOMAIN]), "Service description not set"

    @property
    def allowed_actions(self) -> list:
        raise NotImplementedError

    def action(self, action_name: str, *args: tuple, **kwargs: dict) -> dict:
        """
        Action handler. We pass here every action, make checks and then grab result from requested action.

        :param action_name: Action name to redirect to. Action function should be named in convention `action_{name}`
        :param args: Args
        :param kwargs: Kwargs
        :return: Dict with response
        """
        log.info(f"Called action {action_name} on {self.SERVICE_NAME} service provider")

        action_name = f"action_{action_name}"

        # check if function: is in allowed actions, exists and is callable
        func = getattr(self, action_name, None)
        if (action_name not in self.allowed_actions) or (not func) or (not callable(func)):
            raise ModuleNotFoundError(f"Action {action_name} does not exist for this service provider")

        # we only accept dicts as a return value, because we serialize everything to JSON afterwards on endpoint side
        result = func(*args, **kwargs)
        if not isinstance(result, dict):
            raise TypeError(f"Action result is not in required type. Expected dict, got {str(type(result))}")

        return result
