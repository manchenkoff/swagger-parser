import prance

from .specification import *


class ParserException(Exception):
    """
    Base parser exception class.
    Throws when any error occurs.
    """
    pass


class InfoBuilder:
    @staticmethod
    def _create_license(license_data: Optional[dict]) -> Optional[License]:
        if license_data is None:
            return None

        data = {
            "name": license_data['name'],
            "url": license_data.get('url'),
        }

        return License(**data)

    @staticmethod
    def _create_contact(contact_data: Optional[dict]) -> Optional[Contact]:
        if contact_data is None:
            return None

        data = {
            "name": contact_data.get('name'),
            "url": contact_data.get('url'),
            "email": contact_data.get('email'),
        }

        return Contact(**data)

    def build(self, info_data: dict) -> Info:
        info_builder_dict = {
            "title": info_data['title'],
            "version": info_data['version'],
            "description": info_data.get('description'),
            "terms_of_service": info_data.get('termsOfService'),
            "license": self._create_license(info_data.get('license')),
            "contact": self._create_contact(info_data.get('contact')),
        }

        return Info(**info_builder_dict)


class ServerBuilder:
    @staticmethod
    def _build_server(server_info: dict) -> Server:
        data = {
            "url": server_info['url'],
            "description": server_info.get('description'),
            "variables": server_info.get('variables', {}),
        }

        return Server(**data)

    def build_server_list(self, server_data_list: list) -> List[Server]:
        return [self._build_server(item) for item in server_data_list]


class Parser:
    info_builder: InfoBuilder
    server_builder: ServerBuilder

    def __init__(self, info_builder: InfoBuilder, server_builder: ServerBuilder) -> None:
        self.info_builder = info_builder
        self.server_builder = server_builder

    def load_specification(self, data: dict) -> Specification:
        """
        Load Swagger Specification object from a file or a remote URI.
        :param data: JSON (dict) of specification data
        :return: Specification object
        """

        version = data['openapi']

        info = self.info_builder.build(data['info'])
        servers = self.server_builder.build_server_list(data['servers'])

        return Specification(
            openapi=version,
            info=info,
            servers=servers
        )


def parse(uri: str) -> Specification:
    """
    Parse specification document by URL or filepath
    """
    swagger_resolver = prance.ResolvingParser(
        uri,
        backend='openapi-spec-validator',
        strict=False,
        lazy=True
    )

    try:
        swagger_resolver.parse()
    except prance.ValidationError:
        raise ParserException("Swagger specification validation error")

    specification = swagger_resolver.specification

    parser = Parser()

    return parser.load_specification(specification)