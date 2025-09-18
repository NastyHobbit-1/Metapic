from metapicpick.normalize import Normalizer


def test_parse_text_block():
n = Normalizer()
out = n.parse_text_block("Sampler: Euler a, Steps: 30, CFG: 7.5, Seed: 123")
assert out["sampler"] == "Euler a"
assert out["steps"] == 30
assert out["cfg"] == 7.5
assert out["seed"] == 123