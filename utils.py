from flask import request

page = int(request.args.get('page', 1))
page_size = int(request.args.get('page_size', 10))


def pagination(query, page, page_size):
    return query.limit(page_size).offset((page - 1) * page_size)
