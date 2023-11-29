from microdot_asyncio import Microdot
from semver import SemanticVersion
import hardware


info_app = Microdot()
control_api_version = SemanticVersion.from_semver("0.0.0")


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/info
@info_app.get("")
async def get_index(request):
    return {
        "hw_version": hardware.hw_version.to_string(),
        "api_version": control_api_version.to_string(),
        "api": {
            "latest": "v0",
            "versions": {
                "v0": "/api/v0",
            },
        },
    }
