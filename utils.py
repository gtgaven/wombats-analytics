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
        file_list.sort()
        with open(f'{out_dir}/{s}.html', 'w') as out_file:
            out_file.write('<!DOCTYPE html><html><link rel="stylesheet" href="css/styles.css"></head><body>')
            out_file.write(f'''<div>
                <table>
                <caption>{s}</caption>
                <thead>''')
            for page in file_list:
                out_file.write(f'<tr><td><a href="{s}/{page}"><div style="height:100%;width:100%;">{Path(page).stem}</div></a></td></tr>')
            out_file.write('</table></div></body></html')

    with open(f'{out_dir}/career.html', 'w') as out_file:
        file_list = os.listdir(f'{out_dir}/career')
        file_list.sort()
        out_file.write('<!DOCTYPE html><html><link rel="stylesheet" href="css/styles.css"></head><body>')
        out_file.write('''<div>
                <table>
                <caption>All Time Stats</caption>
                <thead>''')
        for page in file_list:
            out_file.write(f'<tr><td><a href="career/{page}"><div style="height:100%;width:100%;">{Path(page).stem}</div></a></td></tr>')
        out_file.write('</table></div></body></html')

    file_list = os.listdir(f'{out_dir}')
    file_list.sort()
    with open(f'{out_dir}/index.html', 'w') as out_file:
        out_file.write('<!DOCTYPE html><html><head><link rel="stylesheet" href="css/styles.css"></head><body>')
        out_file.write('''<div>
                <table>
                <caption>Staaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaats</caption>
                <thead>''')
        for f in file_list:
            if os.path.isfile(f'{out_dir}/{f}'):
                out_file.write(f'<tr><td><a href="{f}"><div style="height:100%;width:100%;">{Path(f).stem}</div></a></td></tr>')
        out_file.write('</table></div></body></html')

