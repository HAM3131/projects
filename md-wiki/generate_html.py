import os
import markdown2
import re
import shutil

def convert_md_to_html(md_content):
    """
    Converts Markdown content to HTML using the markdown2 library.
    """
    return markdown2.markdown(md_content)

def create_hyperlinks(md_content, files, current_file, current_directory, root_directory):
    """
    Converts plain text references to other Markdown files into hyperlinks in the given Markdown content.
    """
    links = {}
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.md'):
                # Create a dictionary of {file_name_without_extension: relative_path_to_html_file}
                file_key = filename.replace('_', ' ').replace('.md', '').lower()
                relative_path = os.path.relpath(os.path.join(dirpath, filename), current_directory).replace(os.sep, '/')
                links[file_key] = relative_path.replace('.md', '.html')

    # Remove current file from links to avoid self-referencing
    current_file_key = os.path.splitext(current_file)[0].replace('_', ' ').lower()
    if current_file_key in links:
        del links[current_file_key]

    def replace_link(match):
        """
        Replace plain text references with HTML hyperlinks.
        """
        text = match.group(0)
        text_key = text.strip().lower()
        if text_key in links:
            return f'<a href="{links[text_key]}">{text}</a>'
        return text

    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in links.keys()) + r')\b', re.IGNORECASE)
    return pattern.sub(replace_link, md_content)

def generate_breadcrumbs(directory, current_file, root_directory):
    """
    Generates HTML for breadcrumb navigation based on the directory structure.
    """
    relative_path = os.path.relpath(directory, root_directory)
    parts = relative_path.split(os.sep)
    breadcrumbs = [('wiki', os.path.join(os.path.relpath(root_directory, directory), 'home.html'))]  # Start with the root as 'wiki'
    path = root_directory
    for part in parts:
        if part and part != '.':  # Ignore empty parts (e.g., for root)
            path = os.path.join(path, part)
            breadcrumbs.append((part, os.path.join(os.path.relpath(path, directory), 'home.html')))
    breadcrumbs.append((os.path.splitext(current_file)[0], ''))

    breadcrumb_html = ''
    for i, (name, link) in enumerate(breadcrumbs):
        if link:
            breadcrumb_html += f'<a href="{link}" class="breadcrumb-link">{name}</a>'
        else:
            breadcrumb_html += f'<span class="breadcrumb-current">{name}</span>'
        if i < len(breadcrumbs) - 1:
            breadcrumb_html += ' &gt; '

    return breadcrumb_html

def generate_toc(md_content):
    """
    Generates a Table of Contents (TOC) with numbered entries for each header in the Markdown content.
    """
    headers = re.findall(r'^(#{1,6})\s+(.*)', md_content, re.MULTILINE)
    toc = []
    header_counters = [0] * 6  # Support up to 6 levels of headers

    for header in headers:
        level = len(header[0]) - 1  # 0-based index
        if level == 0:
            level = 1  # Treating # and ## headers the same
        title = header[1]
        anchor = re.sub(r'\s+', '-', title.lower())
        
        # Increment the current level counter
        header_counters[level] += 1
        
        # Reset lower level counters
        for i in range(level + 1, 6):
            header_counters[i] = 0
        
        # Build the numbering string
        numbering = ".".join(str(num) for num in header_counters[:level + 1] if num > 0)
        
        # Append the TOC item
        toc.append(f'<li style="margin-left: {level * 10}px;">{numbering} <a href="#{anchor}">{title}</a></li>')

    return '\n'.join(toc)

def add_anchors(md_content):
    """
    Adds HTML anchor tags to headers in the Markdown content for linking.
    """
    def anchor_replacer(match):
        header_level = match.group(1)
        header_text = match.group(2)
        anchor_name = re.sub(r'\s+', '-', header_text.lower())
        return f'{header_level} <a name="{anchor_name}" id="{anchor_name}"></a>{header_text}'
    
    md_content = re.sub(r'^(#{1,6})\s+(.*)', anchor_replacer, md_content, flags=re.MULTILINE)
    return md_content

def generate_html_from_template(template_path, page_title, css_path, breadcrumbs, content, sub_pages, toc):
    """
    Generates HTML content by filling in a template with the given parameters.
    """
    with open(template_path, 'r') as template_file:
        template = template_file.read()

    html_content = template.replace('{{PAGE_TITLE}}', page_title)
    html_content = html_content.replace('{{CSS_PATH}}', css_path)
    html_content = html_content.replace('{{BREADCRUMBS}}', breadcrumbs)
    html_content = html_content.replace('{{CONTENT}}', content)
    html_content = html_content.replace('{{SUB_PAGES}}', sub_pages)
    html_content = html_content.replace('{{TOC}}', toc)

    return html_content

def generate_home_page(directory, files, subdirectories, home_content, output_dir, root_directory, ignore_list, template_path):
    """
    Generates the home page for a directory including links to subdirectories and other Markdown files.
    """
    sub_pages = '<ul>'
    for subdir in subdirectories:
        if subdir not in ignore_list:
            description_file = os.path.join(directory, subdir, 'description.txt')
            if os.path.exists(description_file):
                with open(description_file, 'r') as f:
                    description = f.read().strip()
                sub_pages += f'<li><a href="{subdir}/home.html"><b>{subdir.title()}</b> - {description}</a></li>'
            else:
                sub_pages += f'<li><a href="{subdir}/home.html">{subdir.title()}</a></li>'

    for file in files:
        if file != 'home.md' and file not in ignore_list:
            file_name = os.path.splitext(file)[0]
            sub_pages += f'<li><a href="{file_name}.html">{file_name.replace("_", " ").title()}</a></li>'
    sub_pages += '</ul>'

    breadcrumbs = generate_breadcrumbs(directory, 'home.md', root_directory)
    content = convert_md_to_html(home_content)
    toc = generate_toc(home_content)
    css_path = os.path.relpath(os.path.join(root_directory, 'styles.css'), directory).replace(os.sep, '/')
    html_content = generate_html_from_template(template_path, 'Home', css_path, breadcrumbs, content, sub_pages, toc)

    with open(os.path.join(output_dir, 'home.html'), 'w') as f:
        f.write(html_content)

def read_ignore_list(directory):
    """
    Reads a list of files and directories to ignore from an 'ignore.txt' file in the given directory.
    """
    ignore_file = os.path.join(directory, 'ignore.txt')
    if os.path.exists(ignore_file):
        with open(ignore_file, 'r') as f:
            ignore_list = f.read().splitlines()
        return ignore_list
    return []

def process_directory(directory, output_directory, root_directory, template_path):
    """
    Processes a directory to convert all Markdown files to HTML and generates the necessary HTML files for navigation.
    """
    ignore_list = read_ignore_list(directory)

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.md') and f not in ignore_list]
    subdirectories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and not d.startswith('.') and d not in ignore_list]

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    if 'home.md' in files:
        with open(os.path.join(directory, 'home.md'), 'r') as f:
            home_content = f.read()
        home_content = create_hyperlinks(home_content, files, 'home.md', directory, root_directory)
        generate_home_page(directory, files, subdirectories, home_content, output_directory, root_directory, ignore_list, template_path)

    for file in files:
        if file != 'home.md':
            with open(os.path.join(directory, file), 'r') as f:
                md_content = f.read()
            md_content = create_hyperlinks(md_content, files, file, directory, root_directory)
            toc = generate_toc(md_content)
            md_content = add_anchors(md_content)
            breadcrumbs = generate_breadcrumbs(directory, file, root_directory)
            content = convert_md_to_html(md_content)
            page_title = os.path.splitext(file)[0].replace('_', ' ').title()
            css_path = os.path.relpath(os.path.join(root_directory, 'styles.css'), directory).replace(os.sep, '/')
            html_content = generate_html_from_template(template_path, page_title, css_path, breadcrumbs, content, '', toc)
            html_file = os.path.join(output_directory, os.path.splitext(file)[0] + '.html')
            with open(html_file, 'w') as f:
                f.write(html_content)

    for subdir in subdirectories:
        subdir_input = os.path.join(directory, subdir)
        subdir_output = os.path.join(output_directory, subdir)
        process_directory(subdir_input, subdir_output, root_directory, template_path)

def clear_directory(directory):
    """
    Deletes all files and subdirectories from the specified directory.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def add_css(source_directory, output_directory):
    """
    Copies the CSS file from the source directory to the output directory.
    """
    shutil.copyfile(os.path.join(source_directory, 'styles.css'), os.path.join(output_directory, 'styles.css'))

if __name__ == "__main__":
    root_directory = '/home/r0m/notes'  # Change this to your root input directory
    html_src_directory = '/home/r0m/projects/md-wiki/html-source' # Change this to your root html source directory
    output_directory = '/var/www/myfiles'  # Change this to your desired output directory
    template_path = os.path.join(html_src_directory, 'template.html')
    clear_directory(output_directory)
    add_css(html_src_directory, output_directory)
    process_directory(root_directory, output_directory, root_directory, template_path)
