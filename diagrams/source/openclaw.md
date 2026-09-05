# OpenClaw module diagram sources

## D57 — OpenClaw deployed on an EC2 machine

```mermaid
flowchart LR
    Y["You in Telegram"] --> TG["Telegram servers"]
    TG -->|"bot messages"| GW["OpenClaw gateway on EC2, port 18789 loopback only"]
    GW --> AG["Agent: workspace, memory, tools"]
    AG -->|"API key"| GM["Google Gemini API"]
    GM -->|"reply or tool call"| AG
    AG -->|"reply"| GW
    GW --> TG
    L["Your laptop over SSH"] -->|"administer"| GW
```

Text alternative: messages travel from Telegram to the gateway running on the EC2 machine, the agent assembles context and calls Gemini with your API key, tools run on the machine, and the reply returns through Telegram; you administer the gateway only over SSH, since its port is bound to the machine itself.

## D58 — Two layers of identity: the AWS account and the machine

```mermaid
flowchart TD
    R["AWS root user: MFA, no access keys, unused"] -->|"creates"| I["IAM user admin: MFA, daily console work"]
    I -->|"launches"| E["EC2 instance: Ubuntu 24.04"]
    E --> S["Security group: SSH from your IP only"]
    E --> U["ubuntu user: key login, sudo"]
    U -->|"never"| RO["root login: disabled"]
    U -->|"never"| PW["password login: disabled"]
```

Text alternative: on the account side the root user is locked behind MFA and unused while an IAM user does the daily work; on the machine side the security group admits SSH only from you, the ubuntu user logs in with a key and uses sudo, and both root login and password login are disabled.

## D59 — One message through OpenClaw

```mermaid
sequenceDiagram
    participant U as You
    participant T as Telegram
    participant G as Gateway
    participant A as Agent
    participant M as Gemini
    U->>T: message to the bot
    T->>G: deliver to bot connection
    G->>G: allowed sender? pairing or allowlist
    G->>A: message + session
    A->>M: system prompt + memory + conversation
    M-->>A: reply or tool call
    A->>A: run permitted tool, append result
    A->>M: continue until final reply
    M-->>A: final text
    A-->>G: reply
    G-->>T: send as bot
    T-->>U: reply appears
```

Text alternative: the gateway checks that the sender is allowed, hands the message to the agent, which calls Gemini with its context and runs any permitted tool the model requests until a final reply is produced and sent back through Telegram.
