import platform
import subprocess

def _os_notify(title: str, message: str):
    """Zero-dependency cross-platform OS desktop notification."""
    system = platform.system()
    try:
        # Sanitize message for quotes
        safe_msg = message.replace('"', '\\"')
        safe_title = title.replace('"', '\\"')
        if system == "Windows":
            print("Trying Windows notification...")
            # Use PowerShell to show a toast notification using standard Windows Forms
            ps_script = (
                '[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); '
                '$objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon; '
                '$objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information; '
                f'$objNotifyIcon.BalloonTipTitle = "{safe_title}"; '
                f'$objNotifyIcon.BalloonTipText = "{safe_msg}"; '
                '$objNotifyIcon.Visible = $True; '
                '$objNotifyIcon.ShowBalloonTip(10000); '
                'Start-Sleep -s 10; '
                '$objNotifyIcon.Dispose()'
            )
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_script], 
                             creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            print("Windows notification executed.")
    except Exception as e:
        print(f"Failed to show OS notification: {str(e)}")

_os_notify("Noosphere Link", "This is a direct OS notification test from agent telepathy!")
