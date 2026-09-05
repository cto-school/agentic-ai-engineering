# OpenClaw module — Your own always-on assistant on AWS

**Outcome:** OpenClaw, an open-source personal AI assistant, running on an Ubuntu virtual machine
in AWS that you created and hardened yourself, reachable through a Telegram bot you own, and
answering with Google's Gemini through your API key.

The module has two halves. Chapters C2 to C4 are a compact cloud-and-Linux course: open an AWS
account without living as the root user, launch an EC2 instance, log in over SSH, and remove
password and root access. Chapters C5 to C7 install and configure OpenClaw on that machine. The
first half stands alone if all you want is a safe Linux server.

| Chapter | File | You learn | You do |
|---|---|---|---|
| C1 | `01_what_openclaw_is.md` | the gateway, channels, agents, providers; why it needs its own machine | plan the deployment |
| C2 | `02_open_an_aws_account_safely.md` | root user versus IAM user, MFA, the Free plan, budgets | create the account, an admin user and a budget alert |
| C3 | `03_launch_an_ec2_ubuntu_machine.md` | regions, AMIs, instance types, key pairs, security groups | launch Ubuntu 24.04 on a small instance |
| C4 | `04_ssh_in_and_harden_the_machine.md` | SSH keys, the `ubuntu` user, sudo, sshd settings, the firewall | log in, disable root and password login, enable updates |
| C5 | `05_install_openclaw.md` | the installer, onboarding, the gateway as a service | install OpenClaw and see the gateway running |
| C6 | `06_connect_a_telegram_bot.md` | BotFather, tokens, DM pairing, allowlists | create the bot, connect it, approve yourself |
| C7 | `07_gemini_model_and_daily_operation.md` | providers and model ids, the security audit, logs, updates, backups, cost | wire up Gemini, chat, and keep the machine healthy |

Diagrams D57 to D59 in [`diagrams/source/openclaw.md`](../../diagrams/source/openclaw.md).

OpenClaw moves quickly; commands in this module were checked against
[docs.openclaw.ai](https://docs.openclaw.ai) in September 2026. When a wizard prompt differs from
the text, follow the wizard and the documentation.
