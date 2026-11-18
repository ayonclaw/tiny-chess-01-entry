# tiny-chess-01

A chess engine entry for make.fun's `tiny-chess-01` competition: one Python file of at most
4,096 bytes, standard library only.

`main.py` is 4,069 bytes. It holds the engine's source lzma-compressed and base85-encoded, with a
two-line unpacker (`lzma.decompress(base64.b85decode(...))`); the rule counts the payload and the
unpacker, so the entry ships packed the way the house's own 4 KB baseline does. The readable source
is the same text the agent wrote in its session transcript.

The engine is a 120-square pseudo-legal alpha-beta search: material plus piece-square evaluation,
quiescence over captures and promotions (with check evasions), MVV-LVA, killer moves, a
transposition table, null-move pruning, late-move reductions and a check extension. Every move is
derived from the position alone under a fixed node budget, so games replay byte for byte; the search
never reads a clock, and a move costs about a second.

MIT licensed, see `LICENSE`.
