# Open an n8n Cloud account and learn the editor

By the end of this chapter you have a workspace, a Gemini API key stored as a credential, and you
know the six parts of the editor that the next chapters refer to.

## 1. Start the trial

1. Go to [n8n.io](https://n8n.io) and choose **Get started** (the button text changes; look for
   the free trial, not the self-hosting guide).
2. Sign up with an email address, or with Google or GitHub. No card is asked for.
3. Choose a workspace name. It becomes your address: `https://<workspace>.app.n8n.cloud`.
4. Wait a minute while the instance is created, then open it.

What you have: a **14-day trial** of the Pro plan with a limit of 1,000 executions (runs) for the
trial. That is far more than this module uses. When the trial ends the workspace is deleted unless
you subscribe, and you can download your workflows for 90 days afterwards. Chapter N7 shows how to
export them at any time, so nothing you build is lost.

If your instructor provides a self-hosted n8n instead, everything from here on is identical; only
the address differs.

## 2. Get a Gemini API key

1. Open [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and sign in with a Google
   account.
2. **Create API key**. Copy it now; treat it like a password.

The key has a free tier with rate limits that are generous for learning. The models this module
names (`gemini-2.5-flash` and its successors) are fast and cheap; you can pick a stronger one in any
chat-model node later.

## 3. Store it as a credential

Nodes never contain keys directly. They refer to a credential you save once.

1. In the left sidebar choose **Credentials** (in newer versions it is a tab on the **Overview**
   page), then **Create credential**.
2. Search for **Google Gemini(PaLM) Api** and select it.
3. Paste the key into **API Key**. The host stays as the default `https://generativelanguage.googleapis.com`.
4. **Save**. n8n tests it and shows a green tick.

Prefer OpenRouter, as the day notebooks do? Create an **OpenRouter** credential with that key
instead; n8n has an *OpenRouter Chat Model* node that is a drop-in for the Gemini one in every
chapter.

## 4. The editor, six things to find

Create a workflow (**Create workflow** on the Overview page) and locate these before building
anything:

1. **The canvas.** The drawing area. Scroll to zoom, drag the background to pan.
2. **The plus button.** Top right, and on the end of every node's output line. It opens the node
   panel where you search for nodes by name. Typing *agent*, *gemini*, *memory*, *wikipedia* finds
   what the next chapters ask for.
3. **A node's settings.** Double-click any node. Left column is its input, middle is its
   parameters, right is its output. Every field can hold a fixed value or an *expression*.
4. **Execute step / Execute workflow.** Execute step (in the node view) runs one node with the
   input shown. Execute workflow (bottom of the canvas) runs everything from the trigger. Both run in
   *test* mode and show data inline.
5. **Executions.** A tab next to *Editor* at the top. Every run, green or red, with each node's
   data. This is where you look when an agent misbehaves.
6. **The Active switch and Save.** Top right. *Save* stores the drawing. *Active* turns on the
   trigger for real: schedules fire, forms accept submissions, webhooks answer. Until then, only
   test runs happen.

Two more things appear once you add the relevant trigger: a **Chat** button at the bottom of the
canvas (with a Chat Trigger) and a **Test URL / Production URL** pair (with a Form or Webhook
trigger).

## 5. Expressions in one minute

A parameter field is either **Fixed** or **Expression** (toggle above the field). Expressions are
JavaScript inside double braces:

```text
{{ $json.chatInput }}            the field chatInput of the current item
{{ $('Form').item.json.email }}  a field from an earlier node named Form
{{ $now.toFormat('yyyy-MM-dd') }} today's date
```

Drag a field from the input column into a parameter and n8n writes the expression for you. That is
the usual way; typing them is for later.

## Recap

- Sign up at n8n.io: a 14-day Pro trial, no card, workspace deleted afterwards unless you subscribe, so export what you build.
- Get a Gemini key from AI Studio and store it once as a *Google Gemini(PaLM) Api* credential.
- Know the canvas, the plus button, node settings, Execute step versus Execute workflow, the Executions tab, and Save versus Active.
