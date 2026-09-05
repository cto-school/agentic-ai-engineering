# Connect a Telegram bot

A Telegram bot is an account that a program controls. You create one in Telegram, receive a token,
give the token to OpenClaw, and from then on the gateway receives every message sent to the bot and
replies as it. Nobody but you should be able to use it, so the second half of the chapter is about
who is allowed in.

## 1. Create the bot with BotFather

1. In Telegram, open a chat with **@BotFather** (the verified one, with a blue tick).
2. Send `/newbot`.
3. Choose a display name (anything, for example `My Assistant`).
4. Choose a username. It must end in `bot` and be unique, for example `aurora_helper_bot`.
5. BotFather replies with a **token** of the form `123456789:AAH...`. Copy it. It is the password to
   your bot: anyone with it can read and send its messages. If it leaks, `/revoke` in BotFather
   issues a new one.

While you are there, `/setdescription` and `/setuserpic` are optional polish.

## 2. Give the token to OpenClaw

Telegram is configured in the file, not with a login command. Either edit the file or use the
config commands. With the commands, on the server:

```bash
openclaw config set channels.telegram.enabled true
openclaw config set channels.telegram.botToken "123456789:AAH..."
openclaw config set channels.telegram.dmPolicy pairing
openclaw config validate
```

The equivalent in `~/.openclaw/openclaw.json` (open it with `nano ~/.openclaw/openclaw.json`,
Ctrl+O to save, Ctrl+X to leave):

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123456789:AAH...",
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

Alternatively the environment variable `TELEGRAM_BOT_TOKEN` works for the default account. Keep the
token out of chat logs and screenshots.

The gateway watches the file and reconnects on its own. Confirm:

```bash
openclaw channels status
openclaw logs --follow
```

The log shows a successful `getMe` call, which is Telegram acknowledging the token. Ctrl+C to leave
the log.

## 3. Pair yourself

`dmPolicy: "pairing"` means an unknown person who messages the bot receives a **pairing code**
and nothing else; the bot answers them only after you approve the code on the server. Codes expire
after one hour.

1. In Telegram, search for your bot's username and send it `hello`.
2. The bot replies with a pairing code.
3. On the server:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

4. Send `hello` again. This time the agent answers.

Your numeric Telegram user id is now on the allowlist. Anyone else who finds the bot gets a code you
never approve. This is the first of the three security questions from chapter C1, "who can talk to
it", answered.

The other policies exist for other situations: `"allowlist"` refuses unknown senders silently,
`"open"` lets anyone in (and requires you to write `"*"` into the allowlist deliberately), and
`"disabled"` ignores direct messages entirely. Stay on `pairing`.

## 4. Groups (optional, and off by default)

Add the bot to a Telegram group and it does nothing until the group is allowed. Because of
`requireMention: true`, even in an allowed group it answers only when addressed as
`@your_bot_name`. To allow one group: find its chat id in the log when a message arrives (a negative
number starting with `-100`), then add it under `channels.telegram.groups` with the same shape as
the `"*"` entry, and in the group send `/whoami@<bot_username>` to check the bot sees you. Leave
groups alone for now; a personal assistant in a group chat reads everything everyone writes, and
everything it reads can try to steer it.

## 5. Check the loop end to end (diagram D59)

Send the bot three messages: a question, a follow-up that depends on the first, and
`What time is it on your server?`. The first two show that the agent keeps the conversation; the
third makes it run a command, which is the capability chapter C7 puts limits around.

## Recap

- BotFather's `/newbot` gives a token; it goes into `channels.telegram.botToken`, never into a login command.
- `dmPolicy: "pairing"` makes strangers receive a code; `openclaw pairing approve telegram <CODE>` lets you in and nobody else.
- Groups stay off unless allowed and mention-gated; `openclaw channels status` and the log confirm the connection.
