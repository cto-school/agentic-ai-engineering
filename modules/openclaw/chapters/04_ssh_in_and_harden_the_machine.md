# Log in over SSH and harden the machine

You now have a server reachable from the internet. Before it does anything useful it should refuse
every way in except your key. Ubuntu's cloud image already does most of this; this chapter makes it
explicit, verifies it, and adds a firewall and automatic security updates (diagram D58, right
column).

## 1. First login

The Ubuntu image creates one user, **`ubuntu`**, with your key already installed and the right to
become the administrator with `sudo`. The root account exists but has no password and cannot log in.

```powershell
# Windows PowerShell (OpenSSH is built in on Windows 10 and 11)
ssh -i C:\Users\<you>\.ssh\openclaw-key.pem ubuntu@<public-ip>
```

```bash
# macOS and Linux: the key file must be readable by you only, or ssh refuses it
chmod 400 ~/.ssh/openclaw-key.pem
ssh -i ~/.ssh/openclaw-key.pem ubuntu@<public-ip>
```

Answer `yes` to the fingerprint question the first time. The prompt changes to
`ubuntu@ip-172-...:~$`. You are on the server.

On Windows, if ssh complains that the key's permissions are too open, run once:

```powershell
icacls C:\Users\<you>\.ssh\openclaw-key.pem /inheritance:r /grant:r "$env:USERNAME:R"
```

Save yourself typing for the rest of the module by adding an entry to `~/.ssh/config`
(`C:\Users\<you>\.ssh\config` on Windows) so that `ssh openclaw` is enough:

```text
Host openclaw
    HostName <public-ip>
    User ubuntu
    IdentityFile ~/.ssh/openclaw-key.pem
```

## 2. Update everything

```bash
sudo apt update && sudo apt upgrade -y
```

`sudo` runs one command as the administrator; the `ubuntu` user may use it without a password. If
the upgrade mentions a new kernel, `sudo reboot`, wait a minute, and log in again.

## 3. Verify and fix the SSH server settings

Ask the SSH daemon what it is actually doing:

```bash
sudo sshd -T | grep -Ei 'permitrootlogin|passwordauthentication|pubkeyauthentication|kbdinteractive'
```

You want:

```text
permitrootlogin no            (or prohibit-password, which also refuses root passwords)
passwordauthentication no
pubkeyauthentication yes
kbdinteractiveauthentication no
```

Whatever it shows, make the settings explicit so a future package update cannot loosen them. Ubuntu
reads extra files from `/etc/ssh/sshd_config.d/`; create one:

```bash
sudo tee /etc/ssh/sshd_config.d/99-hardening.conf > /dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
EOF
sudo sshd -t && sudo systemctl restart ssh
```

`sshd -t` checks the syntax first; if it prints nothing, the restart is safe. **Keep this terminal
open** and test from a second terminal that `ssh openclaw` still works before you close the first.
If the second login fails, fix the file from the first session.

Prove that passwords are refused: from your laptop,

```bash
ssh -o PubkeyAuthentication=no ubuntu@<public-ip>
```

must answer `Permission denied (publickey)` without ever asking for a password.

## 4. Root: confirm it is locked

```bash
sudo passwd -S root
```

`root L ...` means locked (no usable password). If you ever see `P`, lock it:

```bash
sudo passwd -l root
```

Nobody logs in as root on this machine, ever. When a guide tells you to run something as root, use
`sudo` in front of it. If you need a root shell for several commands, `sudo -i` gives one, and
`exit` leaves it.

Should OpenClaw get its own user instead of `ubuntu`? The OpenClaw documentation recommends a
separate operating-system user when the machine is shared with anything else. This machine exists
only for OpenClaw, so `ubuntu` is acceptable for the module. If you prefer the separation:

```bash
sudo adduser --disabled-password --gecos "" openclaw
sudo mkdir -p /home/openclaw/.ssh && sudo cp ~/.ssh/authorized_keys /home/openclaw/.ssh/
sudo chown -R openclaw:openclaw /home/openclaw/.ssh && sudo chmod 700 /home/openclaw/.ssh
```

Then log in as `openclaw@<public-ip>` for chapters C5 to C7. Note it has no `sudo`; do system tasks
as `ubuntu`.

## 5. Firewall on the machine

The security group already allows only SSH from your IP. Add a second layer on the machine itself
so that a mistake in the console does not expose anything:

```bash
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status verbose
```

Expected: default deny incoming, allow outgoing, `OpenSSH ALLOW IN Anywhere`. The OpenClaw gateway
port 18789 is never opened; it listens on the machine itself only, and you administer OpenClaw
through SSH.

## 6. Automatic security updates

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades     # answer Yes
```

Security patches now install themselves nightly. Optionally, `sudo apt install -y fail2ban` bans
addresses that fail SSH repeatedly; with key-only login it is belt and braces.

## 7. The checklist

```bash
sudo sshd -T | grep -Ei 'permitrootlogin|passwordauthentication'   # both no
sudo passwd -S root                                                 # L
sudo ufw status                                                     # active, OpenSSH only
systemctl is-enabled unattended-upgrades                            # enabled
```

## Recap

- Log in as `ubuntu` with the `.pem` key; use `sudo` for administration and never log in as root.
- Make `PermitRootLogin no` and `PasswordAuthentication no` explicit in `sshd_config.d`, test from a second terminal before closing the first, and prove a password login is refused.
- Two firewalls (security group and ufw) admit only SSH from you; unattended-upgrades keeps the machine patched.
