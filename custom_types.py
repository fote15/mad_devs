from typing import TypedDict, List


class ParentDict(TypedDict):
    tag_id: int
    name: str
    classes_list: List[str]


class WrappedResult(TypedDict):
    element: object
    el_clean: object
    parents_list: List[ParentDict]