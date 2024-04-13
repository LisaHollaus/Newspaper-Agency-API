from .subscriber import Subscriber


# editor inherits Subscriber
class Editor(Subscriber):
    def __init__(self, ID: int, name: str, address: str):
        super().__init__(ID, name, address)
        # also inherits issue_list and newspaper_list
