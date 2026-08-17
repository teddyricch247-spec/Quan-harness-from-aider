from unittest.mock import MagicMock

from aider.mdstream import MarkdownStream


def make_stream():
    """A MarkdownStream with a mocked-out Live display and no update throttling."""
    mdstream = MarkdownStream()
    mdstream.live = MagicMock()
    mdstream._live_started = True
    return mdstream


def update(mdstream, text, final=False):
    mdstream.when = 0  # defeat the min_delay throttle
    mdstream.update(text, final=final)


def long_markdown(num_paras, suffix=""):
    """Markdown long enough that some lines scroll out of the live window."""
    return "\n\n".join(f"para {i}" for i in range(num_paras)) + suffix


def test_live_window_repaints_without_new_stable_lines():
    mdstream = make_stream()

    text = long_markdown(20)
    update(mdstream, text)
    assert mdstream.printed  # some lines left the live window and were printed

    # Appending to the last line doesn't add any new stable lines, but the
    # live window still has to be repainted to show the new text.
    mdstream.live.reset_mock()
    update(mdstream, text + " and more")

    assert mdstream.live.update.call_count == 1
    mdstream.live.console.print.assert_not_called()


def test_live_window_shows_all_lines_before_it_fills_up():
    mdstream = make_stream()

    # Fewer rendered lines than live_window, so nothing is stable yet and the
    # live window has to show everything rendered so far.
    text = long_markdown(3)
    rendered = mdstream._render_markdown_to_lines(text)
    assert 0 < len(rendered) < mdstream.live_window

    update(mdstream, text)

    assert not mdstream.printed
    mdstream.live.console.print.assert_not_called()
    shown = mdstream.live.update.call_args[0][0]
    assert len(shown.plain.splitlines()) == len(rendered)


def test_final_update_stops_live_without_new_stable_lines():
    mdstream = make_stream()

    text = long_markdown(20)
    update(mdstream, text)

    # Pretend everything has already been printed above the live window, so the
    # final update has no new stable lines to emit. It must still tear down Live.
    live = mdstream.live
    mdstream.printed = mdstream._render_markdown_to_lines(text)
    update(mdstream, text, final=True)

    live.stop.assert_called_once()
    assert mdstream.live is None
