
def get_openapi_config():
    openapi_config = {
        "openapi": "3.0.0",
        "info": {
            "title": "Femicide Media Project API",
            "version": "1.0.0",
            "description": "This is the API for the FMedia project.",
            "termsOfService": "https://example.com/terms/",
            "contact": {
                "name": "crojasu",
                "email": "catalina@welevelup.org",
            },
            "license": {
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
            },
        },
        "externalDocs": {
            "description": "Find more info here ",
            "url": "https://example.com/docs/",
        },
        "x-logo": {
            "url": "/data/logo.png",
            "backgroundColor": "#FFFFFF",  # Optional background color
            "altText": "FMedia Logo",  # Optional alternative text
        },
        "x-defaultModelsExpandDepth": 0,
        "x-defaultModelExpandDepth": 1,
        "x-explorerUrl": "/docs",
        "x-showExtensions": True,
        "x-whitelisted": True
    }
    return openapi_config
