from bs4 import BeautifulSoup
from typing import Generator

def wrap_in_parents_v2(first_result, fragment, soup):
    working_fragment = fragment

    # Ensure the fragment has a parent
    if not working_fragment.parent:
        return False
    parents_list = []
    working_parent = working_fragment.parent
    while working_parent.parent:
        working_parent.find().parent['tag_id'] = id(working_parent.find().parent)
        parents_list.append({
            'tag_id': id(working_parent.find().parent),
            'name': working_parent.find().parent.name,
           # 'el': working_parent.find().parent
            })
        working_parent = working_parent.parent

    for parent in parents_list:
        new_tag = soup.new_tag(parent['name'])

        # Wrap the current fragment in the new tag
        first_result = first_result.wrap(new_tag)
    return {
        'element': first_result,
        'el_clean': fragment,
        'parents_list': parents_list[::-1],
    }


def get_first_element(soup):
    """
    Traverse the HTML to find the deepest, first non-string child recursively.
    """
    current = soup
    if current.get_text().strip().replace(' ', '').replace('\n', '').replace('\r', '') == '':
        return False
    while True:
        # Get the first non-string child
        children = [child for child in current.children if not isinstance(child, str)]
        if not children:
            break  # No more children, deepest element found
        current = children[0]
    return current


def split_message(source: str, max_len: int = 10) -> Generator[str, None, None]:
    soup = BeautifulSoup(html, 'html.parser')
    elements_result_tree = []
    result = None
    while get_first_element(soup):
        fragment = get_first_element(soup)
        first_result = fragment
        # Wrap the fragment recursively in parent tags
        first_result = wrap_in_parents_v2(first_result, fragment, soup)
        first_result['element'].extract()

        elements_result_tree.append(first_result)
        if first_result['el_clean'].get_text().strip().replace(' ', '').replace('\n', '').replace('\r', '') != '':
            yield first_result['element']

html = '''
<p>
  <b>
     <span>
         <b>
             <a href="https://www.google.com/">Google search</a>
         </b>
        </span>
    <ul>
      <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</li>
      <li>Ut enim ad minim veniam, quis nostrud exercitation ullamco.</li>
      <li>Duis aute irure dolor in reprehenderit in voluptate.</li>
    </ul>
  </b>
</p>
'''

if __name__ == '__main__':
    for chunk in split_message(html, max_len=20):
        print('chunk')
        print(chunk)
