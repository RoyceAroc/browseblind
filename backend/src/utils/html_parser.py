from bs4 import BeautifulSoup, Comment, NavigableString


def get_xpath(element):
    parts = []
    for parent in element.parents:
        siblings = parent.find_all(element.name, recursive=False)
        if len(siblings) > 1:
            index = siblings.index(element) + 1
            parts.append(f"{element.name}[{index}]")
        else:
            parts.append(element.name)
        element = parent
    parts.reverse()
    return "/" + "/".join(parts)


def get_new_html(old_html):
    global html_code
    html_code = ""
    soup = BeautifulSoup(old_html, "html.parser")
    global elements
    elements = []
    for element in soup.find_all(True):

        def list_append(clickable, elem, xpath=None):
            global html_code
            global elements
            if clickable:
                elements.append(get_xpath(elem))
                if len(list(element.children)) == 1:
                    html_code += (
                        "<clickable id='task-"
                        + str(len(elements))
                        + "'>"
                        + elem.get_text(strip=True).strip()
                        + "</clickable>"
                    )
            else:
                text = elem.strip()
                if len(text) != 0:
                    html_code += " " + elem.strip() + " "

        tag_name = element.name.lower()
        if tag_name == "a" or tag_name == "button":
            list_append(True, element)
        elif tag_name == "script" or tag_name == "style" or tag_name == "noscript":
            continue
        else:
            roy = list(element.children)
            for idx in range(len(roy)):
                if isinstance(roy[idx], NavigableString) and not isinstance(
                    roy[idx], Comment
                ):
                    curr_elem = list(element.children)[idx]
                    list_append(False, curr_elem)
    return html_code, elements
