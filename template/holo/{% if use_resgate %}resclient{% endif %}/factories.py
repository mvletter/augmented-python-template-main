from polyfactory.factories.pydantic_factory import ModelFactory

from holo.resclient.models import AccessResGateModel, GetResGateModel


class GetResGateModelFactory(ModelFactory[GetResGateModel]): ...


class AccessResGateModelFactory(ModelFactory[AccessResGateModel]): ...
