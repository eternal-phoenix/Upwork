japanese = ('Japanese', 'Japan', 'translate from japanese', 'translate to japanese')
chinese = ('Chinese', 'China', 'translate from chinese', 'translate to chinese')
stop = ('senior',)


def get_category(title: str, text: str) -> str:

    category = None

    if any([item.lower() in title.lower() for item in japanese]) or any([item.lower() in text.lower() for item in japanese]):
        category = 'japanese'
    elif any([item.lower() in title.lower() for item in chinese]) or any([item.lower() in text.lower() for item in chinese]):
        category = 'chinese'
    elif any([item.lower() in title.lower() for item in stop]) or any([item.lower() in text.lower() for item in stop]):
        category = 'stop'

    return category

