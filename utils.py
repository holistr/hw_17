def pagination(query, page, page_size):
    return query.limit(page_size).offset((page - 1) * page_size)
