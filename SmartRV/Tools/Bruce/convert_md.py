import markdown2
from update_version import get_versions
from datetime import datetime

def convert_md_to_html(md_file_path):
    # Read the Markdown file
    with open(md_file_path, 'r') as file:
        md_content = file.read()

    # Convert Markdown to HTML
    html_content = markdown2.markdown(md_content)

    return html_content


def update_version_in_file(file_path, new_version):
    """
    Update the version number in the specified md file.

    :param file_path: Path to the file to be updated.
    :param new_version: New version number as a string.
    """
    try:
        current_date = datetime.now().strftime("%B %d, %Y")  # Format: Month Day, Year

        # Read the file contents
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Update the version number and release date
        for i, line in enumerate(lines):
            if line.strip().startswith("- **Version Number**:"):
                lines[i] = f"- **Version Number**: {new_version}\n"
            elif line.strip().startswith("- **Release Date**:"):
                lines[i] = f"- **Release Date**: {current_date}\n"

        # Write the updated contents back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)

        return True
    except Exception as e:
        print(f"Error updating file: {e}")
        return False



if __name__ == '__main__':

    from_dir = "."

    new_v = get_versions(from_dir)

    file_path = './data/about.md'

    update_version_in_file(file_path, new_v['version'])

    html_content = convert_md_to_html(file_path)
    print(html_content)
    with open('./data/about.html', 'w') as file:
        file.write(html_content)

