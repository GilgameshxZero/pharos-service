import requests

from subprocess import PIPE, Popen

def print_file_from_url(file_url,
                        kerberos,
                        file_name,
                        color=False):
    """
    Example usage:
    print_file_from_url(
        file_url="https://arxiv.org/ftp/arxiv/papers/1903/1903.05641.pdf",
        kerberos="twang6"
        file_name="arxiv_paper"
    )
    """
    r = requests.get(file_url)

    lpr = Popen([
        'lpr',
        '-l', # send without formatting
        '-H', 'printers.mit.edu', # endpoint
        '-P', 'color' if color else 'bw',
        '-U', kerberos,
        '-T', file_name
        ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    lpr_out = lpr.communicate(input=r.content)

    return lpr_out
