import hashlib
import uuid

from starlette import status


async def test_segment_headers(test_client, mocker) -> None:
    """
    Test Segment headers are set correctly.
    """
    vg_user_uuid = str(uuid.uuid4())
    identity = hashlib.sha256(vg_user_uuid.encode()).hexdigest()

    headers = {
        "X-SEGMENT-USER-ID": identity,
        "X-SEGMENT-EVENT": "my-important-event",
        "X-SEGMENT-CONTEXT-APP-NAME": "my-incredible-service",
        "X-SEGMENT-CONTEXT-A-B-C-D": "contextvar",
    }

    mocked_track = mocker.patch("holo.segment.middleware.analytics.track")

    get_url = "/docs"
    response = await test_client.get(get_url, headers=headers)
    assert response.status_code == status.HTTP_200_OK, response.json()

    context = {
        "app": {
            "name": "my-incredible-service",
        },
        "a": {
            "b": {
                "c": {
                    "d": "contextvar",
                },
            },
        },
    }
    mocked_track.assert_called_once_with(user_id=identity, event="my-important-event", context=context)
