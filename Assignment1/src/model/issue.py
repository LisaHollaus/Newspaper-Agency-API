
class Issue(object):
    def __init__(self, releasedate, issue_id: int = 0, released: bool = False, editor_id: int = None, pages: int = 0, newspaper_id=None):
        self.issue_id: int = issue_id
        self.releasedate = releasedate
        self.released: bool = released
        self.editor_id = editor_id
        self.pages: int = pages
        self.newspaper_id = newspaper_id  # the newspaper the issue is from

    def __eq__(self, other):
        return (self.releasedate == other.releasedate) and (self.released == other.released) and (self.editor_id == other.editor_id) and (self.pages == other.pages) and (self.newspaper_id == other.newspaper_id)
