from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, List, Tuple, Union

from dataset import DataSetInterface, DataSetItem


class DataSet(DataSetInterface):
    """
    Implementation of DataSetInterface.
    Stores DataSetItem objects, indexed by unique item.name.
    """

    def __init__(self, items: Union[List[DataSetItem], Tuple[DataSetItem, ...]] = []):
        super().__init__(items)
        self._items: Dict[str, DataSetItem] = {}
        self._insert_order: List[str] = []

        # If initial items were provided, add them in given order
        for it in items:
            self += it

    def __setitem__(self, name: str, id_content: Tuple[int, Any]):
        if not isinstance(name, str):
            raise TypeError("name must be str")

        if not (isinstance(id_content, tuple) and len(id_content) == 2):
            raise TypeError("id_content must be a tuple (id, content)")

        _id, content = id_content
        if not isinstance(_id, int):
            raise TypeError("id must be int")

        # As required: create DataSetItem first, then add
        self += DataSetItem(name, _id, content)

    def __iadd__(self, item: DataSetItem):
        if not isinstance(item, DataSetItem):
            raise TypeError("Only DataSetItem can be added")

        name = item.name

        # If name is new, remember insertion order
        if name not in self._items:
            self._insert_order.append(name)

        # Overwrite existing item with same name
        self._items[name] = item
        return self

    def __delitem__(self, name: str):
        if name not in self._items:
            raise KeyError(name)

        del self._items[name]
        # also remove from insertion order
        self._insert_order.remove(name)

    def __contains__(self, name: str) -> bool:
        return name in self._items

    def __getitem__(self, name: str) -> DataSetItem:
        if name not in self._items:
            raise KeyError(name)
        return self._items[name]

    def __and__(self, dataset: DataSetInterface) -> DataSetInterface:
        # Intersection: names are the key; take items from self
        result = DataSet()
        # keep default iteration settings from DataSetInterface; tests set them later anyway
        for name, item in self._items.items():
            if name in dataset:
                result += item
        return result

    def __or__(self, dataset: DataSetInterface) -> DataSetInterface:
        # Union: take all from self, then add/overwrite by items from dataset
        result = DataSet()

        # add self items first (keep same objects)
        for item in self:
            result += item

        # then add items from dataset (overwrite by name)
        for item in dataset:
            # item is a DataSetItem (because dataset.__iter__ yields items)
            result += item

        return result

    def __iter__(self) -> Iterator[DataSetItem]:
        # Determine base order: insertion order or sorted
        if self.iterate_sorted:
            items = list(self._items.values())
            if self.iterate_key == self.ITERATE_SORT_BY_ID:
                items.sort(key=lambda it: it.id, reverse=self.iterate_reversed)
            else:
                items.sort(key=lambda it: it.name, reverse=self.iterate_reversed)
        else:
            items = [self._items[name] for name in self._insert_order]
            if self.iterate_reversed:
                items.reverse()

        return iter(items)

    def filtered_iterate(self, filter: Callable[[str, int], bool]):
        # Iterate as in __iter__ order, but only yield items passing filter(name, id)
        for item in self:
            if filter(item.name, item.id):
                yield item

    def __len__(self) -> int:
        return len(self._items)
