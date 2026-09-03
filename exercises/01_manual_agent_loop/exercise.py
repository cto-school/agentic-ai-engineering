"""Complete the bounded manual agent loop. No SDK is required."""


def run_agent(model, tools, messages, max_steps=4):
    """Return the final text.

    model(messages) returns either:
      {"type": "final", "text": "..."}
      {"type": "tool", "name": "...", "arguments": {...}}

    A tool result must be appended before asking the model again.
    Reject unknown tools and stop after max_steps.
    """
    raise NotImplementedError("TODO: implement observe-dispatch-append-terminate")

