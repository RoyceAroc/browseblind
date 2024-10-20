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


def get_new_html(old_html, event_listeners):
    global html_code
    html_code = ""
    soup = BeautifulSoup(old_html, "html.parser")
    global elements
    elements = []
    for element in soup.find_all(True):

        def list_append(clickable, elem, xpath=None, input_status=False):
            global html_code
            global elements
            if input_status:
                elements.append({"type": "input", "xpath": get_xpath(elem)})
                input_attributes = elem.attrs
                input_attributes_str = " ".join(
                    f"data='{value}'" for key, value in input_attributes.items()
                )
                html_code += (
                    "<input id='input-"
                    + str(len(elements))
                    + f"' {input_attributes_str}></input>"
                )
            else:
                if clickable:
                    if xpath is not None:
                        elements.append({"type": "click", "xpath": xpath})
                    else:
                        elem_inner_text = elem.get_text(strip=True).strip()
                        elements.append({"type": "click", "xpath": get_xpath(elem)})
                        if len(list(element.children)) == 1:
                            html_code += (
                                "<clickable id='click-"
                                + str(len(elements))
                                + "'>"
                                + elem_inner_text
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
        elif tag_name == "input" or tag_name == "textarea" or tag_name == "select":
            list_append(False, element, None, True)
        else:
            roy = list(element.children)
            for idx in range(len(roy)):
                if isinstance(roy[idx], NavigableString) and not isinstance(
                    roy[idx], Comment
                ):
                    curr_elem = list(element.children)[idx]
                    list_append(False, curr_elem)
            curr_elem_xpath = get_xpath(element)
            for event in event_listeners:
                if event["xpath"] == curr_elem_xpath:
                    list_append(True, element, curr_elem_xpath)
    return html_code, elements
