import datetime
from functools import wraps
from inspect import Parameter, Signature, signature
from typing import List, Optional
from fastapi import Query
from utils.constants import DT_X, Q_X
import datetime
import uuid


class ContentQueryChecker:
    def __init__(self, cols=None, actions=None, exclude: List[str] = []):
        # Ensure `self._cols` handles both tuples and single column names
        self._cols = []
        for item in cols:
            if isinstance(item, tuple) and len(item) == 2:
                self._cols.append(item)
            elif isinstance(item, str):  # Handle unexpected string values
                self._cols.append((item, None))


        #print(f"Processed columns in ContentQueryChecker: {self._cols}")

        
        self._actions = actions
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # if kwargs.get("sort"):
            #     print(f"Sort values before processing: {kwargs['sort']}")

            # Filter out dynamically added parameters, keeping only original params
            orig_sig = signature(func)
            orig_param_names = [p.name for p in orig_sig.parameters.values()]
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in orig_param_names}
            
            # Pass only the original arguments to the function
            return func(*args, **filtered_kwargs)
        
        # Get the original signature
        sig = signature(func)
        orig_params = list(sig.parameters.values())
        
        # Separate keyword-only parameters (e.g., db)
        keyword_only_params = [p for p in orig_params if p.kind == Parameter.KEYWORD_ONLY]
        sort_str = f"^({'|'.join([f'{x[0]}|-{x[0]}' for x in self._cols])})(,({'|'.join([f'{x[0]}|-{x[0]}' for x in self._cols])}))*$" if self._cols else None

        q_str = "|".join([x[0] for x in self._cols if x[0] != 'password']) if self._cols else None
        
        # New parameters to add (all optional)
        new_params = [
            Parameter('offset', Parameter.KEYWORD_ONLY, annotation=int, default=Query(0, ge=0)),
            Parameter('limit', Parameter.KEYWORD_ONLY, annotation=int, default=Query(100, gt=0)),
            Parameter('fields', Parameter.KEYWORD_ONLY, annotation=Optional[List[str]], default=Query(None, regex=f'({q_str})$')),
            Parameter('q', Parameter.KEYWORD_ONLY, annotation=Optional[List[str]], default=Query(None, regex=Q_X.format(cols=f'({q_str})') if q_str else r'^[\w]+$|^[\w]+:[\w]+$')),
            Parameter('sort', Parameter.KEYWORD_ONLY, annotation=Optional[List[str]], default=Query(None, explode=True)),
        ]
        
        # Add column-based query parameters
        if self._cols:
            for item in self._cols:
                if isinstance(item, tuple):
                    col_name, col_type = item  # Unpack normally if it's a tuple
                else:
                    col_name = item  # If it's a string, just use it
                    col_type = None  # Default type to None or handle it differently

                if col_name == 'password':  # Skip password field if present
                    continue
                elif col_type == datetime.datetime:
                    new_params.append(
                        Parameter(
                            col_name, 
                            Parameter.KEYWORD_ONLY, 
                            annotation=Optional[str], 
                            default=Query(None, description=f"Filter by {col_name} (e.g., '2023-01-01')")
                        )
                    )
                elif col_type == uuid.UUID:
                    new_params.append(
                        Parameter(
                            col_name, 
                            Parameter.KEYWORD_ONLY, 
                            annotation=Optional[str], 
                            default=Query(None, description=f"Filter by {col_name} (UUID)")
                        )
                    )
                elif col_type == dict:
                    new_params.append(
                        Parameter(
                            col_name, 
                            Parameter.KEYWORD_ONLY, 
                            annotation=Optional[str], 
                            default=Query(None, description=f"Filter by {col_name} (JSON string)")
                        )
                    )
                else:
                    new_params.append(
                        Parameter(
                            col_name, 
                            Parameter.KEYWORD_ONLY, 
                            annotation=Optional[col_type] if col_type else Optional[str], 
                            default=Query(None, description=f"Filter by {col_name}")
                        )
                    )
        
        # Construct the new signature: keyword-only params first, then new params
        final_params = keyword_only_params + new_params
        wrapper.__signature__ = Signature(final_params)
        return wrapper










def str_to_datetime(value: str) -> datetime.datetime:
    # Convert string to datetime. Implement as needed for your project.
    return datetime.datetime.fromisoformat(value)




from config.settings import settings
import sqlalchemy.types as types
# from cls import Upload
import pathlib


class Upload:
    def __init__(self, file, upload_to, size=None):
        self.file = file
        self.upload_to = upload_to
        self.size = size

    def _ext(self):
        return pathlib.Path(self.file.filename).suffix


class File(types.TypeDecorator):
    impl = types.String
    cache_ok = False

    def __init__(self, *args, upload_to, size=None, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.upload_to = upload_to
        self.size = size

    def process_bind_param(self, value, dialect):
        if not value:
            return None
        file = Upload(value, upload_to=self.upload_to, size=self.size)
        url = file.save()
        return url

    def process_result_value(self, value, dialect):
        if value:
            if value[:3] == 'S3:':
                return settings.AWS_S3_CUSTOM_DOMAIN + value[3:]
            return settings.BASE_URL + value[3:]
        else:
            return None
