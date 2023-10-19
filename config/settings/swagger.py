SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {"Token": {"type": "apiKey", "name": "Authorization", "in": "header"}},
    "SHOW_COMMON_EXTENSIONS": False,
    # To hide model definition from swagger and only show APIs, we need to replace ReferencingSerializerInspector with
    # InlineSerializerInspector. More details: https://github.com/axnsan12/drf-yasg/issues/281
    "DEFAULT_FIELD_INSPECTORS": [
        "drf_yasg.inspectors.CamelCaseJSONFilter",
        "drf_yasg.inspectors.InlineSerializerInspector",
        "drf_yasg.inspectors.RelatedFieldInspector",
        "drf_yasg.inspectors.ChoiceFieldInspector",
        "drf_yasg.inspectors.FileFieldInspector",
        "drf_yasg.inspectors.DictFieldInspector",
        "drf_yasg.inspectors.SimpleFieldInspector",
        "drf_yasg.inspectors.StringDefaultFieldInspector",
    ],
}
