from bs4 import BeautifulSoup, NavigableString
from typing import Generator
import click

MAX_LEN = 170


class MessageSplitError(Exception):
    """Custom exception for errors during message splitting."""
    pass

def wrap_in_parents_v2(first_result, fragment, soup):
    working_fragment = fragment

    # Ensure the fragment has a parent
    if not working_fragment.parent:
        return {
        'element': first_result,
        'el_clean': fragment,
        'parents_list': [],
    }
    parents_list = []
    working_parent = working_fragment.parent
    while working_parent.parent:
        working_parent.find().parent['tag_id'] = id(working_parent.find().parent)

        # print('working_parent.find(class_=True).parent')
        # print(working_parent.find(class_=True).parent)

        classes_list = []
        if working_parent.find().has_attr("class"):
            classes_list = working_parent.find().parent['class']
        parents_list.append({
            'tag_id': id(working_parent.find().parent),
            'name': working_parent.find().parent.name,
            'classes_list': classes_list,
            # 'el': working_parent.find().parent
            })
        working_parent = working_parent.parent

    for parent in parents_list:
        new_tag = soup.new_tag(parent['name'])
        new_tag['tag_id'] = parent['tag_id']

        if len(parent['classes_list']):
            new_tag['class'] = []
        for class_name in parent['classes_list']:
            new_tag['class'].append(class_name)

        # Wrap the current fragment in the new tag
        first_result = first_result.wrap(new_tag)
    # print('first_result !!!')
    # print(first_result)
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

    # print('current')
    # print(current)

    first_index = 0
    for ind,element in enumerate(soup.children):
        if str(element).strip().replace('\n','') =="":
            first_index += 1
        if ind == first_index and isinstance(element, NavigableString) and element.strip():
            return element


    if current.get_text().strip().replace(' ', '').replace('\n', '').replace('\r', '') == '':
        return False
    while True:
        # Get the first non-string child
        children = [child for child in current.children if not isinstance(child, str)]
        if not children:
            break  # No more children, deepest element found
        current = children[0]
    return current


def find_common_parent(parents_list_1, parents_list_2):
    """
    Finds the deepest common parent tag based on tag_ids from two parent lists.
    """
    # Create sets from the tag_ids in both parents lists
    set_1 = set([parent['tag_id'] for parent in parents_list_1])
    set_2 = set([parent['tag_id'] for parent in parents_list_2])

    # Find common tag_ids
    common_tag_ids = set_1 & set_2

    if not common_tag_ids:
        return None

    # Find the deepest common parent by comparing the position of tag_id
    for parent_1 in reversed(parents_list_1):
        if parent_1['tag_id'] in common_tag_ids:
            return parent_1

    return None


def find_adding_element(tag, element):
    index_of_element = 0
    for ind, parent in enumerate(element['parents_list']):
        if (parent['tag_id'] == tag):
            index_of_element = ind

    result = element['element'].find_all()[index_of_element]
    return result

def find_index_to_add(el1,common_parent):
    index_to_add = 0

    for ind, parent in enumerate(el1['element'].find_all()):

        if parent.get('tag_id') and (int(parent.get('tag_id')) == common_parent['tag_id']):
            return ind
    for ind, par in enumerate(el1['parents_list']):
        if par['tag_id'] == common_parent['tag_id']:
            index_to_add = ind

            return index_to_add
def combine_elements(el1, adding_element):
    """
    Combines the result element and the adding_element based on the deepest common parent.
    """
    result_soup = BeautifulSoup(str(el1['element']), 'html.parser')
    adding_element_soup = BeautifulSoup(str(adding_element['element']), 'html.parser')
    common_parent = find_common_parent(el1['parents_list'], adding_element['parents_list'])
    if not common_parent:
        index_to_add = 0
        result_soup.append(adding_element['element'])
    else:
        index_to_add = find_index_to_add(el1, common_parent)
        adding_elemet = find_adding_element(common_parent['tag_id'], adding_element)
        result_soup.find_all()[index_to_add].append(adding_elemet)

    re = {
        'element':result_soup,
        'parents_list':adding_element['parents_list']
    }
    return re


def remove_tag_id_attributes(html_content):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(str(html_content), "html.parser")

    # Remove all 'tag_id' attributes
    for tag in soup.find_all(True):  # find_all(True) gets all tags
        if 'tag_id' in tag.attrs:
            del tag['tag_id']

    # Return the modified HTML as a string
    return soup

def split_message(source: str, max_len: int = 10) -> Generator[str, None, None]:
    soup = BeautifulSoup(source, 'html.parser')
    elements_result_tree = []
    result = None

    while_index = 0
    fragment = get_first_element(soup)

    while fragment:
        while_index+=1


        first_result = fragment

        first_result = wrap_in_parents_v2(first_result, fragment, soup)

        if not first_result:
            yield first_result
        else:
            first_result['element'].extract()

        elements_result_tree.append(first_result)


        first_result_clean_text = first_result['el_clean'].get_text().strip().replace(' ', '').replace('\n', '').replace('\r', '')

        if first_result_clean_text != '':
            if not result:
                result = first_result
            else:
                clean_last_result = result['element']

                save_last_first_result = {key: value for key, value in first_result.items()}
                save_last_first_result['element'] = first_result['element'].__copy__()

                combined = combine_elements(result, first_result)
                last_combined = combined
                now_combined = remove_tag_id_attributes(last_combined['element'])
                a = True

                if (len(str(now_combined))) > max_len and clean_last_result:
                    a = False

                    result = save_last_first_result

                    cleaned = str(remove_tag_id_attributes(clean_last_result)).replace('\n','')
                    len_cleaned = len(str(remove_tag_id_attributes(cleaned)).replace('\n',''))
                    if len_cleaned > max_len:
                        raise MessageSplitError(f"fragment {remove_tag_id_attributes(cleaned)} - {len_cleaned} exceeds MAX_LEN {max_len} ")
                    yield cleaned



                if a:
                    result = combined
                #result = combined
                #    clean_last_result = result['element']
        fragment = get_first_element(soup)

    cleaned = str(remove_tag_id_attributes(result['element'])).replace('\n','')
    if len(cleaned) > max_len:
        raise MessageSplitError(
            f"fragment {remove_tag_id_attributes(cleaned)} - {len(cleaned)} exceeds MAX_LEN {max_len} ")

    yield cleaned





@click.command()
@click.option('--max-len', default=MAX_LEN, help='Maximum length of message fragments.')
@click.argument('file_path', type=click.Path(exists=True))
def main(max_len: int, file_path: str):
    """
    Reads the input file, splits the content, and prints the fragments with their lengths.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        source = file.read()

    try:
        for i, chunk in enumerate(split_message(source, max_len), start=1):
            print(f"fragment #{i}: {len(str(chunk))} chars - {str(chunk)}")
    except MessageSplitError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
