import os
from pathlib import Path

def format_float(percentage):
    return '{0:.3f}'.format(percentage)


def export_webapp_landing_pages(out_dir: str, seasons):
    try:
        os.remove(f'{out_dir}/index.html')
    except OSError:
        pass

    seasons.sort()
    for s in seasons:
        file_list = os.listdir(f'{out_dir}/{s}')
        with open(f'{out_dir}/{s}.html', 'w') as out_file:
            out_file.write('<!DOCTYPE html><html><body>')
            for page in file_list:
                out_file.write(f'<a href="{s}/{page}">{page}</a><br>')
            out_file.write('</body></html')

    file_list = os.listdir(f'{out_dir}')
    file_list.sort()
    with open(f'{out_dir}/index.html', 'w') as out_file:
        out_file.write('<!DOCTYPE html><html><body>')
        for f in file_list:
            if os.path.isfile(f'{out_dir}/{f}'):
                out_file.write(f'<a href="{f}">{Path(f).stem}</a><br>')
        out_file.write('</body></html')

