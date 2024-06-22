import os
import markdown2

def convert_md_to_html(md_content):
    return markdown2.markdown(md_content)

def create_hyperlinks(md_content, files, output_dir):
    for file in files:
        file_name = os.path.splitext(file)[0]
        md_content = md_content.replace(file_name.replace('_', ' '), f'<a href="{output_dir}/{file_name}.html">{file_name.replace("_", " ")}</a>')
    return md_content

def generate_home_page(directory, files, subdirectories, home_content, output_dir):
    table_of_contents = '<ul>'
    for subdir in subdirectories:
        description_file = os.path.join(directory, subdir, 'description.txt')
        subdir_output = os.path.join(output_dir, subdir)
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read().strip()
            table_of_contents += f'<li><a href="{subdir_output}/home.html">{description}</a></li>'
        else:
            table_of_contents += f'<li><a href="{subdir_output}/home.html">{subdir}</a></li>'
    
    for file in files:
        if file != 'home.md':
            file_name = os.path.splitext(file)[0]
            table_of_contents += f'<li><a href="{output_dir}/{file_name}.html">{file_name.replace("_", " ")}</a></li>'
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
        home_content = create_hyperlinks(home_content, files, output_directory)
        generate_home_page(directory, files, subdirectories, home_content, output_directory)
    
    for file in files:
        if file != 'home.md':
            with open(os.path.join(directory, file), 'r') as f:
                md_content = f.read()
            md_content = create_hyperlinks(md_content, files, output_directory)
            html_content = convert_md_to_html(md_content)
            html_file = os.path.splitext(file)[0] + '.html'
            with open(os.path.join(output_directory, html_file), 'w') as f:
                f.write(html_content)
    
    for subdir in subdirectories:
        subdir_input = os.path.join(directory, subdir)
        subdir_output = os.path.join(output_directory, subdir)
        process_directory(subdir_input, subdir_output)

if __name__ == "__main__":
    root_directory = '/home/r0m/research'  # Change this to your root input directory
    output_directory = '/home/r0m/generated_html'  # Change this to your desired output directory
    process_directory(root_directory, output_directory)
