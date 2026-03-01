from pywebpush import webpush, WebPushException
from mythme.model.config import WebpushConfig


def do_push(config: WebpushConfig, subscription: dict[str, str | dict[str, str]]):
    try:
        webpush(
            subscription_info=subscription,
            data='{ "message": "Mary had a little lamb, with a nice mint jelly" }',
            vapid_private_key=config.private_keyfile,
            vapid_claims={
                "sub": f"mailto:{config.mailto}",
            },
        )
    except WebPushException as ex:
        print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
        # Mozilla returns additional information in the body of the response.
        if ex.response is not None and ex.response.json():
            extra = ex.response.json()
            print(
                "Remote service replied with a {}:{}, {}",
                extra.code,
                extra.errno,
                extra.message,
            )
