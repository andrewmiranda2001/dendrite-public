from typing import List, Tuple
from myers import diff
import dendrite.interface.types as types

def diff_note_content(original_content: List[types.Content], new_text: str) -> List[types.Content]:
    # get og content for diffing
    original_lines = []
    for content in original_content:
        if content.status != types.ContentStatus.DELETED:
            original_lines.extend(content.text.split('\n'))
    
    new_lines = new_text.split('\n')
    diff_result: List[Tuple[str, str]] = diff(original_lines, new_lines)

    result_content: List[types.Content] = []
    lines_from_new_text = 0  # Track how many lines we've taken from new_text
    
    for operation, line in diff_result:
        if operation == 'r':  # delete - line only in original, skip it
            pass
        lines_from_new_text += 1
        if operation == 'e':  # equal - line exists in both
            result_content.append(types.Content(
                text=line,
                status=types.ContentStatus.STAGED
            ))
        elif operation == 'i':  # insert - line only in new text
            result_content.append(types.Content(
                text=line,
                status=types.ContentStatus.ADDED
            ))
        else:
            raise ValueError(f"Unknown diff operation: {operation}")
        
    
    if lines_from_new_text != len(new_lines):
        raise ValueError(f"Myers diff algorithm failed to process all lines. Expected {len(new_lines)}, processed {lines_from_new_text}")
    
    return result_content

def apply_content_diff(original_content: List[types.Content], new_text: str) -> Tuple[List[types.Content], bool]:
    current_text = "\n".join([
        content.text for content in original_content 
        if content.status != types.ContentStatus.DELETED
    ])
    
    if current_text.strip() == new_text.strip():
        return original_content, False
    
    new_content = diff_note_content(original_content, new_text)
    return new_content, True

def merge_consecutive_content(content_list: List[types.Content]) -> List[types.Content]:
    """
    Merge consecutive content items with the same status to reduce fragmentation.
    
    Args:
        content_list: List of Content objects
        
    Returns:
        Merged list with consecutive same-status items combined
    """
    if not content_list:
        return content_list
    
    merged = [content_list[0]]
    
    for content in content_list[1:]:
        last = merged[-1]
        
        # If same status and both are text (not empty), merge them
        if (last.status == content.status and 
            last.text.strip() and content.text.strip()):
            
            # Merge the text
            merged[-1] = types.Content(
                text=last.text + "\n" + content.text,
                status=last.status
            )
        else:
            merged.append(content)
    
    return merged

def content_list_to_storage_string(content_list: List[types.Content]) -> str:
    text_parts = []
    for content in content_list:
        if content.status != types.ContentStatus.DELETED and content.text.strip():
            text_parts.append(content.text)
    
    return "\n".join(text_parts)