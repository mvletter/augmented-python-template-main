from sqlalchemy.sql.functions import ReturnTypeFromArgs


class unaccent(ReturnTypeFromArgs):
    inherit_cache = False
