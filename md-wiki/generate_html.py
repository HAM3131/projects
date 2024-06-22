import os
import markdown2
import re
import shutil

def convert_md_to_html(md_content):
    return markdown2.markdown(md_content)

def create_hyperlinks(md_content, files, output_dir, current_file):
    # Generate relative links for each file
    links = {file_name.replace('_', ' '): f'{file_name}.html' for file_name in [os.path.splitext(f)[0] for f in files]}
    
    # Remove current file from links
    current_file_name = os.path.splitext(current_file)[0].replace('_', ' ')
    if current_file_name in links:
        del links[current_file_name]
    
    def replace_link(match):
        text = match.group(0)
        text_key = text.strip().lower()
        if text_key in links:
            return f'<a href="{links[text_key]}">{text}</a>'
        return text
    
    # Match words surrounded by word boundaries
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in links.keys()) + r')\b', re.IGNORECASE)
    return pattern.sub(replace_link, md_content)

def generate_home_page(directory, files, subdirectories, home_content, output_dir):
    table_of_contents = '<ul>'
    for subdir in subdirectories:
        description_file = os.path.join(directory, subdir, 'description.txt')
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read().strip()
            table_of_contents += f'<li><a href="{subdir}/home.html">{description}</a></li>'
        else:
            table_of_contents += f'<li><a href="{subdir}/home.html">{subdir}</a></li>'
    
    for file in files:
        if file != 'home.md':
            file_name = os.path.splitext(file)[0]
            table_of_contents += f'<li><a href="{file_name}.html">{file_name.replace("_", " ")}</a></li>'
    table_of_contents += '</ul>'
    
    html_content = convert_md_to_html(home_content) + table_of_contents
    with open(os.path.join(output_dir, 'home.html'), 'w') as f:
        f.write(html_content)

def process_directory(directory, output_directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.md')]
    subdirectories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    if 'home.md' in files:
        with open(os.path.join(directory, 'home.md'), 'r') as f:
            home_content = f.read()
        home_content = create_hyperlinks(home_content, files, output_directory, 'home.md')
        generate_home_page(directory, files, subdirectories, home_content, output_directory)
    
    for file in files:
        if file != 'home.md':
            with open(os.path.join(directory, file), 'r') as f:
                md_content = f.read()
            md_content = create_hyperlinks(md_content, files, output_directory, file)
            html_content = convert_md_to_html(md_content)
            html_file = os.path.join(output_directory, os.path.splitext(file)[0] + '.html')
            with open(html_file, 'w') as f:
                f.write(html_content)
    
    for subdir in subdirectories:
        subdir_input = os.path.join(directory, subdir)
        subdir_output = os.path.join(output_directory, subdir)
        process_directory(subdir_input, subdir_output)

def clear_output_directory(output_directory):
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    os.makedirs(output_directory)

if __name__ == "__main__":
    root_directory = '/home/r0m/projects/md-wiki/md-source'  # Change this to your root input directory
    output_directory = '/home/r0m/projects/md-wiki/html-output'  # Change this to your desired output directory
    clear_output_directory(output_directory)
    process_directory(root_directory, output_directory)
