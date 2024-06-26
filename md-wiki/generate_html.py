import os
import markdown2
import re
import shutil

def convert_md_to_html(md_content):
    return markdown2.markdown(md_content)

def create_hyperlinks(md_content, files, current_file):
    links = {file_name.replace('_', ' '): f'{file_name}.html' for file_name in [os.path.splitext(f)[0] for f in files]}
    
    current_file_name = os.path.splitext(current_file)[0].replace('_', ' ')
    if current_file_name in links:
        del links[current_file_name]
    
    def replace_link(match):
        text = match.group(0)
        text_key = text.strip().lower()
        if text_key in links:
            return f'<a href="{links[text_key]}">{text}</a>'
        return text
    
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in links.keys()) + r')\b', re.IGNORECASE)
    return pattern.sub(replace_link, md_content)

def generate_breadcrumbs(directory, current_file, root_directory):
    relative_path = os.path.relpath(directory, root_directory)
    parts = relative_path.split(os.sep)
    breadcrumbs = [('wiki', os.path.join(os.path.relpath(root_directory, directory), 'home.html'))]  # Start with the root as 'wiki'
    path = ''
    for part in parts:
        if part and part != '.':  # Ignore empty parts (e.g., for root)
            path = os.path.join(path, part)
            breadcrumbs.append((part, os.path.join(os.path.relpath(path, root_directory), 'home.html')))
    breadcrumbs.append((os.path.splitext(current_file)[0], ''))

    breadcrumb_html = '<nav class="breadcrumbs">'
    for i, (name, link) in enumerate(breadcrumbs):
        if link:
            breadcrumb_html += f'<a href="{link}" class="breadcrumb-link">{name}</a>'
        else:
            breadcrumb_html += f'<span class="breadcrumb-current">{name}</span>'
        if i < len(breadcrumbs) - 1:
            breadcrumb_html += ' &gt; '
    breadcrumb_html += '</nav>'

    return breadcrumb_html

def generate_home_page(directory, files, subdirectories, home_content, output_dir, root_directory):
    table_of_contents = '<ul>'
    for subdir in subdirectories:
        description_file = os.path.join(directory, subdir, 'description.txt')
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read().strip()
            table_of_contents += f'<li><a href="{subdir}/home.html"><b>{subdir.title()}</b> - {description}</a></li>'
        else:
            table_of_contents += f'<li><a href="{subdir}/home.html">{subdir.title()}</a></li>'

    for file in files:
        if file != 'home.md':
            file_name = os.path.splitext(file)[0]
            table_of_contents += f'<li><a href="{file_name}.html">{file_name.replace("_", " ").title()}</a></li>'
    table_of_contents += '</ul>'

    breadcrumbs = generate_breadcrumbs(directory, 'home.md', root_directory)
    header = generate_header('home.md', directory, root_directory)
    html_content = f"<div class='container'>{header + breadcrumbs + convert_md_to_html(home_content) + table_of_contents}</div></body>"
    with open(os.path.join(output_dir, 'home.html'), 'w') as f:
        f.write(html_content)

def generate_header(file_name, current_directory, root_directory):
    title = os.path.splitext(file_name)[0].replace('_', ' ').title()
    relative_path_to_root = os.path.relpath(root_directory, current_directory)
    css_path = os.path.join(relative_path_to_root, 'styles.css').replace(os.sep, '/')
    header_html = f'''
    <head>
        <title>{title}</title>
        <link rel="stylesheet" type="text/css" href="{css_path}">
    </head>
    <body>
    '''
    return header_html

def process_directory(directory, output_directory, root_directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.md')]
    subdirectories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and not d.startswith('.')]

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    if 'home.md' in files:
        with open(os.path.join(directory, 'home.md'), 'r') as f:
            home_content = f.read()
        home_content = create_hyperlinks(home_content, files, 'home.md')
        generate_home_page(directory, files, subdirectories, home_content, output_directory, root_directory)

    for file in files:
        if file != 'home.md':
            with open(os.path.join(directory, file), 'r') as f:
                md_content = f.read()
            md_content = create_hyperlinks(md_content, files, file)
            breadcrumbs = generate_breadcrumbs(directory, file, root_directory)
            header = generate_header(file, directory, root_directory)
            html_content = f"<div class='container'>{header + breadcrumbs + convert_md_to_html(md_content) + '</div></body>'}"
            html_file = os.path.join(output_directory, os.path.splitext(file)[0] + '.html')
            with open(html_file, 'w') as f:
                f.write(html_content)

    for subdir in subdirectories:
        subdir_input = os.path.join(directory, subdir)
        subdir_output = os.path.join(output_directory, subdir)
        process_directory(subdir_input, subdir_output, root_directory)

def clear_directory(directory):
    """
    Deletes all files and subdirectories from the specified directory.

    :param directory: The path to the directory to be cleared.
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
    shutil.copyfile(os.path.join(source_directory, 'styles.css'), os.path.join(output_directory, 'styles.css'))

if __name__ == "__main__":
    root_directory = '/home/r0m/notes'  # Change this to your root input directory
    html_src_directory = '/home/r0m/projects/md-wiki/html-source' # Change this to your root html source directory
    output_directory = '/var/www/myfiles'  # Change this to your desired output directory
    clear_directory(output_directory)
    add_css(html_src_directory, output_directory)
    process_directory(root_directory, output_directory, root_directory)
