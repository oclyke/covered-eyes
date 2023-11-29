from microdot_asyncio import Microdot
import os

shards_app = Microdot()


def shardEdgeByName(name):
    return {
        "node": {
            "name": f"{name}",
        },
        "cursor": f"{name}",
    }


def init_shards_app(shards_source_dir):
    @shards_app.get("")
    async def get_shards(request):
        shard_names = list(os.listdir(shards_source_dir))
        total = len(shard_names)

        if total == 0:
            return {
                "total": 0,
                "edges": [],
                "pageInfo": {
                    "endCursor": None,
                    "hasNextPage": False,
                },
            }

        # compute the edges
        edges = list(map(lambda name: shardEdgeByName(name), shard_names))

        # return the data
        return {
            "total": len(shard_names),
            "edges": edges,
            "pageInfo": {
                "endCursor": edges[-1]["cursor"],
                "hasNextPage": False,
            },
        }

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/shards/<uuid> -d $'def frames(l):\n\twhile True:\n\t\tyield None\n\t\tprint("hello world")\n\n'
    @shards_app.put("/<uuid>")
    async def put_shard(request, uuid):
        # shards are immutable once published, therefore if the specified UUID
        # exists on the filesystem it does not need to be written again
        path = f"{persistent_dir}/shards/{uuid}"
        try:
            os.stat(path)
        except:
            with open(path, "w") as f:
                f.write(request.body)
