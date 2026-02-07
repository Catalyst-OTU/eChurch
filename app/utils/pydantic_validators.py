def check_non_empty_and_not_string(v):
    if isinstance(v, str) and (v.strip() == '' or v.strip().lower() == 'string'):
        raise ValueError(f'Field should not be empty "string"')
    return v
