class BaseConfig:
    DEBUG = True
    TESTING = False


class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    TESTING = True
