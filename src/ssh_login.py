import paramiko
from typing import Tuple, Dict, Any


def try_ssh_login(host: str,
                  username: str,
                  password: str,
                  port: int = 22,
                  timeout: int = 10) -> Tuple[bool, str]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=timeout,
        )
        return True, "Login successful!"
    except paramiko.AuthenticationException:
        return False, "Authentication failed – bad username or password."
    except paramiko.SSHException as exc:
        return False, f"SSH error: {exc}"
    except Exception as exc:
        return False, f"Connection failed: {exc}"
    finally:
        client.close()


def _run_remote_command(client: paramiko.SSHClient,
                       command: str,
                       timeout: int = 15) -> Tuple[int, str, str]:
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    rc = stdout.channel.recv_exit_status()
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    return rc, out, err


def collect_system_utilization(host: str,
                               username: str,
                               password: str,
                               port: int = 22,
                               timeout: int = 10) -> Tuple[bool, Dict[str, Any]]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=timeout,
        )
    except paramiko.AuthenticationException:
        return False, {"error": "Authentication failed"}
    except Exception as exc:
        return False, {"error": f"Connection failed: {exc}"}

    cmds = {
        "uptime": "uptime",
        "memory": "free -m",
        "disk":   "df -h --output=source,fstype,size,used,avail,pcent,target -x tmpfs -x devtmpfs",
        "cpu":    "top -bn1 | head -n 5",
    }

    results: Dict[str, Any] = {}
    for name, cmd in cmds.items():
        rc, out, err = _run_remote_command(client, cmd, timeout=timeout)
        results[name] = {"output": out} if rc == 0 else {"error": err or f"Exit {rc}"}

    client.close()
    return True, results