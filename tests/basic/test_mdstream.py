from types import SimpleNamespace
from aider.mdstream import MarkdownStream


class LiveStub:
    def __init__(self):
        self.update_calls = []
        self.printed_calls = []
        self.console = SimpleNamespace(
            print=lambda value: self.printed_calls.append(value),
        )

    def update(self, value):
        self.update_calls.append(value)

    def stop(self):
        pass


def test_update_preserves_all_lines_shorter_than_live_window():
    rendered_lines = [
        "line1\n",
        "line2\n",
        "line3\n",
        "line4\n",
    ]

    stream = MarkdownStream()
    stream.live_window = 5
    stream.when = 0
    stream.min_delay = 0
    stream._live_started = True
    stream.live = LiveStub()
    stream._render_markdown_to_lines = lambda _text: list(rendered_lines)

    stream.update("ignored text", final=False)

    assert len(stream.live.update_calls) == 1
    assert len(stream.live.printed_calls) == 0

    rendered = stream.live.update_calls[0]
    rendered_text = getattr(rendered, "plain", None) or str(rendered)

    assert rendered_text.splitlines() == [
        "line1",
        "line2",
        "line3",
        "line4",
    ]


def test_update_emits_stable_lines_when_longer_than_live_window():
    rendered_lines = [
        f"line{i}\n" for i in range(1, 9)
    ]

    stream = MarkdownStream()
    stream.live_window = 5
    stream.when = 0
    stream.min_delay = 0
    stream._live_started = True
    stream.live = LiveStub()
    stream._render_markdown_to_lines = lambda _text: list(rendered_lines)

    stream.update("ignored text", final=False)

    assert len(stream.live.update_calls) == 1
    assert len(stream.live.printed_calls) == 1

    printed = stream.live.printed_calls[0]
    printed_text = getattr(printed, "plain", None) or str(printed)
    assert printed_text.splitlines() == ["line1", "line2", "line3"]

    rendered = stream.live.update_calls[0]
    rendered_text = getattr(rendered, "plain", None) or str(rendered)
    assert rendered_text.splitlines() == ["line4", "line5", "line6", "line7", "line8"]
