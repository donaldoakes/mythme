from mythme.model.program import Program
from mythme.model.query import Criterion, Operator, Paging, Query, Sort


def parse_params(params: dict[str, str]) -> Query:
    criteria: list[Criterion] = []
    for key, value in params.items():
        if key in ["sort", "offset", "limit", "desc", "debug"]:
            continue
        val = value
        op: Operator = "="
        if val.startswith(">="):
            val = val[2:]
            op = ">="
        elif val.startswith("<="):
            val = val[2:]
            op = "<="
        elif val.startswith(">"):
            val = val[1:]
            op = ">"
        elif val.startswith("<"):
            val = val[1:]
            op = "<"
        elif val.startswith("IN"):
            val = val[2:]
            op = "IN"
        elif val.startswith("BETWEEN"):
            val = val[7:]
            op = "BETWEEN"
        elif val.startswith("LIKE"):
            val = val[4:]
            op = "LIKE"
        criteria.append(Criterion(name=key, value=val, operator=op))

    sort = Sort(name="start")
    if "sort" in params:
        sort_name = params["sort"]
        if sort_name in Program.model_fields.keys() or sort_name in [
            "channel",
            "channum",
        ]:
            sort.name = sort_name
        sort.order = "asc"
    if "desc" in params and params["desc"] == "true":
        sort.order = "desc"

    paging = Paging(offset=0, limit=50)
    if "offset" in params and params["offset"].isnumeric():
        os = int(params["offset"])
        if os >= 0:
            paging.offset = os
    if "limit" in params and params["limit"].isnumeric():
        lim = int(params["limit"])
        if lim > 0:
            paging.limit = 500 if lim > 500 else lim

    debug = "debug" in params and params["debug"] == "true"

    return Query(criteria=criteria, sort=sort, paging=paging, debug=debug)
