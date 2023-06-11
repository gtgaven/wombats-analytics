def format_float(percentage):
    return '{0:.3f}'.format(percentage)

def html_header_with_css_styling():
    return '''<!DOCTYPE html>
    <html>
        <head><style>
            table {
                border-collapse: collapse;
                width: 100%;
                color: #333;
                font-family: Arial, sans-serif;
                font-size: 16px;
                text-align: center;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                margin: auto;
                margin-top: 25px;
                margin-bottom: 25px;
            } 
            
            table th {
                background-color: #0087ff;
                color: #fff;
                font-weight: bold;
                padding: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-top: 1px solid #fff;
                border-bottom: 1px solid #ccc;
            }

            table tr:nth-child(even) td {
                background-color: #bfbfbf;
            }

            table tr:hover td {
                background-color: #ffedcc;
            }

            table td {
                background-color: #fff;
                padding: 10px;
                border-bottom: 1px solid #ccc;
                font-weight: bold;
            }

            caption {
                margin-bottom: 1em;
                font-size: 1em;
                font-weight: bold;
                text-align: center;
            }
            </style></head>'''
