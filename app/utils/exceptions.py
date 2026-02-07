from fastapi import HTTPException, status


def http_500_exc_internal_server_error() -> Exception:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Something went wrong! Kindly try again or contact support.",
    )



def raise_exc(loc=None, msg=None, type=None):
    detail = {}
    if loc:
        detail.update({"loc":loc if loc.__class__ in [list, set, tuple] else [loc]})
    if msg:
        detail.update({"msg":msg})
    if msg:
        detail.update({"type":type})
    return [detail]