# Launch an EC2 virtual machine running Ubuntu

**EC2** (Elastic Compute Cloud) rents virtual machines by the hour. You choose an operating system
image, a size, a key for logging in and a firewall, and a minute later you have a Linux server with a
public address. This chapter launches the one OpenClaw will live on.

## The choices, before clicking

| Choice | Pick | Why |
|---|---|---|
| Region | the one from C2 | keep everything in one place |
| Image (AMI) | **Ubuntu Server 24.04 LTS**, 64-bit (x86) | long-term support until 2029; OpenClaw's installer targets it |
| Instance type | **t3.small** (2 vCPU, 2 GB RAM); `t3.medium` (4 GB) if you plan to add browser automation | OpenClaw is a Node.js process; 2 GB runs it, 4 GB is comfortable |
| Key pair | a new one, RSA, `.pem` | the only way in; no passwords |
| Network | SSH allowed from **My IP** only; nothing else open | the gateway port stays private |
| Storage | 20 GiB gp3 | room for Node, models' caches and logs |

Free plan credits cover a `t3.small` running all month with margin. An older `t2.micro` also
works for a first look but will feel slow.

## 1. Launch

1. Signed in as `admin`, search **EC2**, open it, confirm the region at the top right.
2. **Launch instance**.
3. **Name**: `openclaw`.
4. **Application and OS Images**: choose **Ubuntu**, then in the drop-down **Ubuntu Server 24.04
   LTS (HVM), SSD Volume Type**, architecture **64-bit (x86)**. Some tutorials use Arm (`t4g`);
   it is cheaper and also works, but stay on x86 the first time so that every command here matches.
5. **Instance type**: `t3.small`.
6. **Key pair (login)** → **Create new key pair**. Name `openclaw-key`, type **RSA**, format
   **.pem**. Click **Create key pair**; the browser downloads `openclaw-key.pem`. Move it to a
   folder you will remember (`C:\Users\<you>\.ssh\` on Windows, `~/.ssh/` on macOS and Linux).
   There is no way to download it again; if you lose it, you launch a new machine.
7. **Network settings** → **Edit**. *Auto-assign public IP*: Enable. *Firewall (security
   groups)*: Create security group, name `openclaw-ssh`. One inbound rule: type **ssh**, source
   type **My IP**. Nothing else. Do not choose "Anywhere".
8. **Configure storage**: 20 GiB, gp3.
9. **Launch instance**. After a few seconds, **View all instances**. Wait for *Instance state:
   Running* and *Status check: 2/2 checks passed*.
10. Select the instance and copy its **Public IPv4 address** from the details panel. This is
    `<public-ip>` in the rest of the module.

## 2. Two things to know about the address

The public IP changes every time the instance is **stopped** and started again (a reboot keeps
it). For this module that is a minor nuisance: you look it up again in the console. If it bothers
you, allocate an **Elastic IP** (EC2 → Elastic IPs → Allocate → Associate with the instance); it is
fixed for as long as you keep it. AWS charges a small hourly fee for every public IPv4 address,
Elastic or not, which the Free plan credits cover.

Your own IP changes too: when you connect from a different network, SSH will time out. Fix it in
EC2 → **Security Groups** → `openclaw-ssh` → **Edit inbound rules** → set the source to *My IP*
again.

## 3. Stop, start, terminate

- **Stop** (Instance state → Stop instance): the machine is switched off, you pay only for the disk
  (cents per month), and everything on it is kept. Start it again any time.
- **Reboot**: restarts the operating system, keeps the address.
- **Terminate**: deletes the machine and its disk. Irreversible. Use it at the end of the course.

Stop the instance whenever you will not use it for days; the credits last longer.

## Recap

- Ubuntu 24.04 LTS on a `t3.small`, a new `.pem` key pair you keep safe, and a security group that allows SSH from your IP only.
- The public IP changes on stop and start; an Elastic IP fixes it. Your own IP changes too; update the security group's rule.
- Stop the instance when idle, terminate it when finished.
