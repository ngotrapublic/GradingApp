"""Wi-Fi address of this computer and the QR code for phones."""
import io, socket


def lan_ips():
    """LAN address of this computer (no DNS lookups – they can hang on macOS)."""
    ips = set()
    for target in ('10.255.255.255', '192.168.255.255', '8.8.8.8'):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(0.2)
            s.connect((target, 1)); ips.add(s.getsockname()[0]); s.close()
        except OSError:
            pass
    return sorted(ip for ip in ips if not ip.startswith(('127.', '0.')))


def qr_svg(url):
    import segno            # installed by start.command
    bio = io.BytesIO(); segno.make(url, error='m').save(bio, kind='svg', scale=8, border=2)
    return bio.getvalue()


def print_qr(url):
    try:
        import segno
    except ImportError:
        return
    print('\n  Scan with your phone / Quét mã này bằng điện thoại:')
    segno.make(url, error='m').terminal(compact=True, border=2)
