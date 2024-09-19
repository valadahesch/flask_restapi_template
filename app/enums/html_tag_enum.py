class HtmlTag:
    _id = ''
    label = ''

    def __init__(self, _id, label, **kwargs):
        self._id = _id
        self.label = label


class UserInfoHT(HtmlTag):
    head = 'user-info'
    label = '用户信息'
    display_name = ''

    def __init__(self, _id, display_name):
        super().__init__(_id, self.label)
        self.display_name = display_name

    def __repr__(self):
        res = f'<{self.head} id="{self._id}" label="{self.label}" display_name="{self.display_name}"/>'
        return res


class SeProjectHT(HtmlTag):
    head = 'se-project'
    label = 'SE项目管理-项目'
    number = ''
    subject = ''

    def __init__(self, _id, number, subject):
        super().__init__(_id, self.label)
        self.number = number
        self.subject = subject

    def __repr__(self):
        res = f'<{self.head} id="{self._id}" label="{self.label}" subject="{self.subject}"/>'
        return res


class SeProjectTaskHT(HtmlTag):
    head = 'se-project-task'
    label = 'SE项目管理-任务'
    number = ''
    subject = ''

    def __init__(self, _id, number, subject):
        super().__init__(_id, self.label)
        self.number = number
        self.subject = subject

    def __repr__(self):
        res = f'<{self.head} id="{self._id}" label="{self.label}" subject="{self.subject}"/>'
        return res


class SeProjectRecordHT(HtmlTag):
    head = 'se-project-record'
    label = 'SE项目管理-日志'

    def __init__(self, _id):
        super().__init__(_id, self.label)

    def __repr__(self):
        res = f'<{self.head} id="{self._id}" label="{self.label}"/>'
        return res
